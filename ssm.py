import cv2
import ssmbase
import glob
# from PySide2 import QtCore, QtGui
from PyQt5.QtWidgets import QSizePolicy, QWidget, QApplication, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.QtWidgets as qtw
from sklearn.decomposition import PCA
import sklearn.preprocessing as pp
from sklearn.neighbors import NearestNeighbors
import random
from keras.applications.resnet50 import preprocess_input
from keras import backend as K
import tensorflow as tf
import netvlad_tf.nets as nets
import csv
import time
import about
import os
import numpy as np
import tkinter
from tkinter import filedialog
from shutil import copyfile
from matplotlib import pyplot as plt


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

#import matplotlib.pyplot as plt
print ("OpenCV v" + cv2.__version__)

class ssm_MainWindow(ssmbase.Ui_MainWindow):
    """ """
    def setupUi(self, MainWindow):
        """ Sets up the VPR user interface  default parameters."""
        ssmbase.Ui_MainWindow.setupUi(self, MainWindow)

        self.method = 'VGG16'

        self.reference_folder = str()
        self.test_folder = str()
        self.ground_truth_file = str()
        self.recognition_paused = False
        self.recognition_continued = False
        self.recognition_stopped = False


        self.useGpuCheckBox.setChecked(1)

        self.actionAbout.triggered.connect(self.showAboutBox)

        self.textBrowser.append("OpenCV v" + cv2.__version__)
        self.path = None
        # self.actionSave_path.triggered.connect(self.savePath)
        self.stopSignal = False



        # self.targetSigmaLineEdit.setToolTip('A value of -1 adjusts the sigma (standard deviation) to the size set in the field above')
        # self.pixelResLineEdit.setToolTip('In units of pixel. For instance, 0.1 will allow the cloud to move in steps of a minimum of 0.1 pixels')


        # stage I
        self.imageWidthLineEdit_s1.returnPressed.connect(self.refresh_view)
        self.imageHeightLineEdit_s1.returnPressed.connect(self.refresh_view)
        self.vggRadioButton.setDisabled(0)
        self.vggRadioButton.click()
        self.netvladRadioButton.setDisabled(0)
        self.vggRadioButton.toggled.connect(self.refresh_view)
        self.netvladRadioButton.toggled.connect(self.refresh_view)

        # stage II
        self.imageWidthLineEdit_s2.returnPressed.connect(self.refresh_view)
        self.imageHeightLineEdit_s2.returnPressed.connect(self.refresh_view)

        self.candidatesLineEdit.setToolTip('Number of candidates  selected in STAGE I (use 1 to consider that stage only')
        self.candidatesLineEdit.returnPressed.connect(self.refresh_view)

        self.frameTolLineEdit.setToolTip('Number of frames (\u00B1) that are considered as belonging to the same place')
        self.frameTolLineEdit.returnPressed.connect(self.refresh_view)

        self.earlyCutLineEdit.setToolTip('Adds (>0) or subtracts (<0) to the average recognition score, setting the threshold for early cut of candidates. Units are in standard deviations of the score.')
        self.earlyCutLineEdit.returnPressed.connect(self.refresh_view)

        self.prevFramesLineEdit.setToolTip('Number of frames previous to current recognition used to improve recognition (use 0 to disable time correlation)')
        self.prevFramesLineEdit.returnPressed.connect(self.refresh_view)

        # select files
        self.btnLoadReference.clicked.connect(self.search_for_dir_path_reference)
        self.btnLoadTest.clicked.connect(self.search_for_dir_path_query)
        self.btnLoadGroungTruth.clicked.connect(self.search_for_file_path_ground_truth)

        # run
        self.btnCreateDB.clicked.connect(self.create_database)
        self.btnRecognition.clicked.connect(self.recognise_places)

        # controls
        # self.btnPause.clicked.connect(self.pause_recognition)
        self.btnPause.clicked.connect(self.pause_continue)
        # self.btnContinue.clicked.connect(self.continue_recognition)
        self.btnStop.clicked.connect(self.stop_recognition)

        # output
        self.btnSaveOutput.clicked.connect(self.save_output)
        self.btnPRcurves.clicked.connect(self.plot_PR_curves)

        # gpu
        self.useGpuCheckBox.clicked.connect(self.use_gpu)


        # console
        # self.textBrowser.setOpenExternalLinks(False)
        self.textBrowser.setOpenLinks(False)
        self.textBrowser.anchorClicked.connect(self.on_anchor_clicked)
        # self.textBrowser.anchorMouseOver.connect(self.on_anchor_clicked)
        # self.textBrowser.getCursor(self.line_clicked)

        # self.targetSigmaLineEdit.returnPressed.connect(self.refresh_view)

    def showAboutBox(self):
        ab = about.AboutForm()
        ab.exec_()

    def refresh_view(self):
        """ 
        Reads all the parameters currently displayed on the GUI
        """
        try:
            # image sizes
            self.image_size1 = (int(self.imageWidthLineEdit_s1.text()), int(self.imageHeightLineEdit_s1.text()))
            self.image_size2 = (int(self.imageWidthLineEdit_s2.text()), int(self.imageHeightLineEdit_s2.text()))

            # method
            self.select_method()

            # paramaters
            self.ncand = int(self.candidatesLineEdit.text())
            self.ftol = int(self.frameTolLineEdit.text())
            self.npf = int(self.prevFramesLineEdit.text())
            self.ecut = float(self.earlyCutLineEdit.text())

        except Exception as e:
            self.textBrowser.append("Error: " + str(e))

    def image_visualize_reference(self, img_path):
        """
        Visualizes reference image in panel (on the right).

        """

        try:

            pic = cv2.imread(img_path)
            pic = cv2.resize(pic, (224, 224))
            qimage = QtGui.QImage(pic, pic.shape[0], pic.shape[1], 3*pic.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            # time.sleep(0.01)
            pic = QtGui.QPixmap(qimage)  # load picture
            self.referenceImageLabel.setPixmap(pic)
            self.referenceImageLabel.setAlignment(QtCore.Qt.AlignRight)
            self.referenceImageLabel.show()
            # self.textBrowser.append("Visualization refreshed")
            # time.sleep(0.01)

        except Exception as e:
            self.textBrowser.append("Error: " + str(e))

    def image_visualize_query(self, img_path):
        """
        Visualizes test image in panel (on the left).

        """
        try:

            pic = cv2.imread(img_path)
            pic = cv2.resize(pic, (224, 224))
            qimage = QtGui.QImage(pic, pic.shape[0], pic.shape[1], 3*pic.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            # time.sleep(0.01)
            pic = QtGui.QPixmap(qimage)  # load picture
            self.queryImageLabel.setPixmap(pic)
            self.queryImageLabel.setAlignment(QtCore.Qt.AlignLeft)
            self.queryImageLabel.show()
            # self.textBrowser.append("Visualization refreshed")
            # time.sleep(0.01)

        except Exception as e:
            self.textBrowser.append("Error: " + str(e))

    def image_visualize_output(self, img_path):
        """
        Visualizes recognized  image in panel (at the center).

        """
        try:
            pic = cv2.imread(img_path)
            pic = cv2.resize(pic, (224, 224))
            qimage = QtGui.QImage(pic, pic.shape[0], pic.shape[1], 3*pic.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
            # time.sleep(0.01)
            pic = QtGui.QPixmap(qimage)  # load picture
            self.outputImageLabel.setPixmap(pic)
            self.outputImageLabel.setAlignment(QtCore.Qt.AlignLeft)
            self.outputImageLabel.show()
            # self.textBrowser.append("Visualization refreshed")
            # time.sleep(0.01)

        except Exception as e:
            self.textBrowser.append("Error: " + str(e))

    def image_visualize_all(self, query_path, output_path, ref_path):
        """       Visualizes reference, query and output in panel. """

        self.image_visualize_query(query_path)
        self.image_visualize_output(output_path)
        self.image_visualize_reference(ref_path)



    def search_for_dir_path_reference(self):
        import tkinter
        from tkinter import filedialog, Tk
        root = Tk()
        root.withdraw()
        self.reference_folder = filedialog.askdirectory()
        if len(self.reference_folder) != 0:
            # self.refOkLabel.setText(u'\u2713')
            self.refOkLabel.setText(self.reference_folder)
            self.textBrowser.append("Reference image directory selected")
        else:
            return 0

        # get filenames in dir
        dir_fnames = [d for d in os.listdir(self.reference_folder)]
        dir_fnames.sort()

        # visualize image in panel
        self.image_visualize_reference(self.reference_folder + '/' + dir_fnames[0])

        # print(self.reference_folder)

    def search_for_dir_path_query(self):
        import tkinter
        from tkinter import filedialog, Tk
        root = Tk()
        root.withdraw()
        self.test_folder = filedialog.askdirectory()
        if len(self.test_folder) != 0:
            # self.testOkLabel.setText(u'\u2713')
            self.testOkLabel.setText(self.test_folder)

        self.textBrowser.append("Test image directory selected")

        # get filenames in dir
        dir_fnames = [d for d in os.listdir(self.test_folder)]
        dir_fnames.sort()

        # visualize image in panel
        self.image_visualize_query(self.test_folder + '/' + dir_fnames[0])

    def search_for_file_path_ground_truth(self):
        # import tkinter
        # from tkinter import filedialog

        # #initiate tinker and hide window
        main_win = tkinter.Tk()
        main_win.withdraw()
        #
        # main_win.overrideredirect(True)
        # main_win.geometry('0x0+0+0')
        # #
        # main_win.deiconify()
        # main_win.lift()
        # main_win.focus_force()


        # open file selector
        self.ground_truth_file = filedialog.askopenfilename(parent=main_win, initialdir="/", title='Please select a file')

        # close window after selection
        main_win.destroy()


        if len(self.ground_truth_file) != 0:
            # self.groundTruthOkLabel.setText(u'\u2713')
            self.groundTruthOkLabel.setText(self.ground_truth_file)
        # print path
        print(self.ground_truth_file)

    def pause_continue(self):
        if self.btnPause.text() == 'Pause':
            self.recognition_paused = True
            self.recognition_continued = False
            self.btnPause.setText("Continue")
            QApplication.processEvents()
        else:
            self.recognition_paused = False
            self.recognition_continued = True
            self.btnPause.setText("Pause")
            QApplication.processEvents()

    def stop_recognition(self):
        self.recognition_stopped = True

    def reset_controls(self):
        self.recognition_continued = False
        self.recognition_stopped = False
        self.recognition_paused = False

    def save_output(self):
        # open file selector
        # self.ground_truth_file = filedialog.asksaveasfile()
        # define options for opening
        options = {}
        options['defaultextension'] = '.txt'
        # options['filetypes'] = fileTypes
        options['initialdir'] = 'output'
        options['initialfile'] = (self.dataset_name + '_' +  self.method + '-'   # image retrieval method (stage I) \
                                 + str(self.image_size1[0]) + '_'               # stage I image size \
                                 + str(self.image_size2[0]) + '_'               # stage II image size \
                                 + str(self.candidatesLineEdit.text()) + '_'    # number of candidates \
                                 + str(self.frameTolLineEdit.text()) + '_'      # frame tolerance \
                                 + str(self.prevFramesLineEdit.text())     )     # number of previous frames considered in FC
        options['title'] = 'Save default output filename'
        filename = filedialog.asksaveasfile(mode='w', **options)
        copyfile('Live_output.txt', filename.name)

    def create_PR_data(self):
        import csv
        import numpy as np

        # # read output file
        # prec_recall_data = self.pr_file

        img_sep = int(self.frameTolLineEdit.text())
        self.pr_data = []
        for results in self.pr_file:
            with open(results) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                data = []
                for row in csv_reader:
                    data.append(row)

                min_thresh = np.round(float(min(np.asarray(data)[:, 4])), 1)
                max_thresh = np.round(float(max(np.asarray(data)[:, 4])), 1)

                pr_data = []
                for mthresh in np.arange(min_thresh, max_thresh, 0.05):

                    tpcnt = 0  # true positive counter
                    fncnt = 0  # false negative counter
                    fpcnt = 0  # false positive counter
                    accuracy = 0
                    precision = 0
                    recall = 0
                    for r in range(len(data)):
                        file = int(data[r][2])
                        img_no = int(data[r][3])
                        thresh = float(data[r][4])

                        if thresh < mthresh:
                            file = -1

                        if file == -1:
                            fncnt += 1
                            color = '\033[91m'
                            if tpcnt > 0:
                                precision = tpcnt / float(tpcnt + fpcnt)
                                recall = tpcnt / float(tpcnt + fncnt)
                                # print(color + '{:>4}  {:>8}  {:>8}'.format(str(r),
                                #                                            str(np.round(precision * 100, 1)),
                                #                                            str(np.round(recall * 100, 1))))
                        elif np.abs(file - img_no) <= img_sep:  # recognised (true positives)
                            tpcnt += 1
                            color = '\033[92m'
                            precision = tpcnt / float(tpcnt + fpcnt)
                            recall = tpcnt / float(tpcnt + fncnt)
                            # print(color + '{:>4}  {:>8}  {:>8}'.format(str(r),
                            #                                            str(np.round(precision * 100, 1)),
                            #                                            str(np.round(recall * 100, 1))))
                        else:  # wrongly recognised (false positive)
                            fpcnt += 1
                            color = '\033[91m'
                            if tpcnt > 0:
                                precision = tpcnt / float(tpcnt + fpcnt)
                                recall = tpcnt / float(tpcnt + fncnt)
                            # print(color + '{:>4}  {:>8}  {:>8}'.format(str(r),
                            #                                            str(np.round(precision * 100, 1)),
                            #                                            str(np.round(recall * 100, 1))))

                    pr_data.append([np.round(precision * 100, 1) , np.round(recall * 100, 1), np.round(mthresh, 2)])
                    # print(str(np.round(precision * 100, 1)) + "," + str(np.round(recall * 100, 1)) + "," + str(np.round(mthresh, 2)) )
                self.pr_data.append(pr_data)

    def compute_auc(self, data):
        """Area under the curve for Precision-Recall curves"""
        auc = 0
        for i in range(1, len(data)):
            delta_rec = np.abs(data[i, 1] - data[i - 1, 1])
            mid_prec = (data[i, 0] + data[i - 1, 0]) / 2.
            auc += delta_rec * mid_prec
            if i == len(data) - 1:
                if data[i, 1] != 0:
                    auc = auc + data[i, 1]
        return auc

    def plot_PR_curves(self):

        # initiate tinker and hide window
        main_win = tkinter.Tk()
        main_win.withdraw()

        # open file selector
        self.pr_file = filedialog.askopenfilenames(parent=main_win, initialdir="output", title='Please select results file. You can select more than one')

        # close window after selection
        main_win.destroy()

        # get Precision-Recall data generated from output file
        self.create_PR_data()
        # auc = compute_auc(data / 100);

        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True)
        fig.add_subplot(111, frameon=False)
        # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        # fig.set_size_inches(12.81, 6.3)

        cnt = 0
        for pr_data in self.pr_data:
            _pr_data = np.asarray(pr_data)
            precision = _pr_data[:, 0]  # / 100.
            recall = _pr_data[:,1] #/ 100.
            auc = self.compute_auc(_pr_data / 100);
            ax.plot(recall, precision, linestyle='solid', linewidth=3,label=os.path.splitext(os.path.basename(self.pr_file[cnt]))[0] +
                          '(AUC=' + str(np.round(auc, 3))  + ')' )
            cnt += 1

        ax.grid(True, linestyle='dotted')
        # ax.text(0.6, 0.1, "day-left vs. night-right", fontsize=14, bbox=props, transform=ax.transAxes)
        ax.legend(fontsize=16, loc='lower left')
        ax.set_yticks([0.0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        ax.tick_params(axis='both', which='major', labelsize=12)

        plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
        plt.grid(False)
        plt.xlabel("Recall ($\%$)", fontsize=16)
        plt.ylabel("Precision ($\%$)", fontsize=16)
        plt.title("Precision-Recall curves", fontsize=18)
        fig.subplots_adjust(bottom=0.2, top=0.9, left=0.1, right=0.97)

        ax.set_xlim(0, 100)
        ax.set_ylim(0.0, 100)
        plt.show()
        plt.pause(0.01)



    def use_gpu(self):
        if self.useGpuCheckBox.checkState() == 0:
            os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        else:
            pass

    def on_anchor_clicked(self, url):
        print("Line clicked")
        text = str(url.toString())
        if text.startswith('http://www.'):
            # self.textBrowser.setSource(QtCore.QUrl()) #stops the page from changing
            function = text.replace('http://www.', '')
            function = function.split("#", 1)[0]
            img_args = function.split('_')
            dir_args = os.path.split(self.test_folder)[0] + '/'
            self.image_visualize_all(self.test_folder +  '/' +  img_args[0], dir_args + 'Reference/'+ img_args[1], dir_args + 'Reference/'+ img_args[2])

            # if hasattr(self,function):
            #     getattr(self,function)()


    def add_baseline_vgg16(self, fnames,  vgg16_feature_arr, h, w):
        """
        Creates VGG features for Stage I of the system
        :param fnames: List of filenames on which to create features
        :param vgg16_feature_arr: Activations from VGG16 layer
        :param h: Height
        :param w: Width
        :return:
        """
        db_array = []
        im_numbers = []
        for idx, fname in enumerate(fnames):
            vgg16_feature_np = vgg16_feature_arr[idx]
            filter_sel = np.moveaxis(vgg16_feature_np[0, :, :, self.filtered_kernels], 0, -1)

            # count how many cubes there are for current image size
            ncubes = 0
            for cii in range(self.lblk, h - self.lblk, 1):
                for cjj in range(self.lblk, w - self.lblk, 1):
                    ncubes += 1

            max_ncubes = self.max_ncubes
            if ncubes > max_ncubes:
                mask = np.random.choice(ncubes, max_ncubes, replace=False)
            else:
                mask = np.arange(max_ncubes)

            # create descriptors by sliding the layer's activations  vertically and horizontally
            cnt2 = 0
            for cii in range(self.lblk, h - self.lblk, 1):
                for cjj in range(self.lblk, w - self.lblk, 1):
                    # skipt blocks not selected in the mask
                    if cnt2 not in mask:
                        cnt2 += 1
                        continue
                    center = (cii, cjj)
                    block = filter_sel[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                    block_descrip = pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.filtered_kernels)), norm='l2', axis=1).flatten()
                    db_array.append(block_descrip)
                    img_no = self.get_img_no(fname)
                    im_numbers.append(img_no)
                    cnt2 += 1
        print(ncubes, np.asarray(im_numbers).shape[0]/len(fnames))
        return np.asarray(db_array), im_numbers

    def prepare_NetVLAD(self):
        # prepare NetVLAD model
        tf.reset_default_graph()
        image_batch = tf.placeholder(dtype=tf.float32, shape=[None, None, None, 3])

        net_out = nets.vgg16NetvladPca(image_batch)
        saver = tf.train.Saver()

        sess = tf.Session()
        saver.restore(sess, nets.defaultCheckpoint())
        return image_batch, net_out, sess

    def add_baseline_netvlad(self, fnames,  sess, net_out, image_batch):
        """
        Creates NetVLAD features for Stage I of the system
        :param fnames: List of filenames on which to create features
        :param sess: From prepare_NetVLAD()
        :param net_out: From prepare_NetVLAD()
        :param image_batch: From prepare_NetVLAD()
        :return:
        """
        db_array = []
        im_numbers = []
        fnames.sort()
        for idx, fname in enumerate(fnames):
            if idx % 1 == 0:
                print(idx, fname, 'calculating NetVLAD descriptors...')
                self.textBrowser.append(str('{:<5}  {}  {}'.format(idx, fname, 'calculating NetVLAD descriptors...')) )
                QApplication.processEvents()

            fpath = self.ref_dir + fname
            im = cv2.imread(fpath)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            im = cv2.resize(im, self.image_size1, interpolation=cv2.INTER_CUBIC)
            im = np.expand_dims(im, axis=0)

            # get and store descriptor and image number
            descriptor = sess.run(net_out, feed_dict={image_batch: im})
            img_no = self.get_img_no(fname)
            db_array.append(descriptor.flatten())
            im_numbers.append(img_no)
        return db_array, im_numbers

    def prepare_img(self, fpath, image_size):
        im = cv2.imread(fpath)
        img_data = cv2.resize(im, image_size, interpolation=cv2.INTER_CUBIC)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)
        return img_data

    def get_img_no(self, fname):
        """gets the right image number from image filename"""
        img_no = int(''.join(map(str, [int(s) for s in os.path.splitext(fname)[0] if s.isdigit()])))
        return img_no

    def train_pca(self, db_array, geom_array, ns1, ns2):
        """
        Trains PAC models for  stages I and II
        :param db_array: Vectors for stage I
        :param geom_array: Vectors for stage II
        :param ns1: Max number of samples for stage I
        :param ns2: Max number of samples for stage II
        :return pca, pca_geom: pca models
        """


        print("training pca...")
        self.textBrowser.append(str('{}'.format("training pca...")))
        QApplication.processEvents()
        pca = None
        if ns2 > len(geom_array):
            ns2 = len(geom_array)

        if len(db_array) > ns1:
            if self.method == 'NetVLAD':  # pca not needed (self-implemented)
                pass
            elif self.method == 'VGG16':
                # select samples randomly for stage I
                mask = np.random.choice([False, True], len(db_array), p=[1 - ns1 / len(db_array), ns1 / len(db_array)])
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array[np.where(mask ==True)])

            # select samples randomly for stage II
            mask_geom = np.random.choice([False, True], len(geom_array), p=[1 - ns2 / len(geom_array), ns2 / len(geom_array)])
            pca_geom = PCA(n_components=self.num_dim2, svd_solver='full', whiten=True).fit(geom_array[np.where(mask_geom == True)])
        else:
            if self.method == 'NetVLAD':  # pca not needed (self-implemented)
                pass
            elif self.method == 'VGG16':
                # perform pca on all samples
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array)

            if len(geom_array) > ns2:
                # select samples randomly for stage II
                mask_geom = np.random.choice([False, True], len(geom_array), p=[1 - ns2 / len(geom_array), ns2 / len(geom_array)])
                pca_geom = PCA(n_components=self.num_dim2, svd_solver='full', whiten=True).fit(geom_array[np.where(mask_geom == True)])
            else:
                # perform pca on all samples                                                           len(db_array) / len(geom_array)])
                pca_geom = PCA(n_components=self.num_dim2, svd_solver='full', whiten=True).fit(geom_array)

        return pca, pca_geom

    def calc_pca(self,  dir_fnames,  dset_name):
        """Calculates the pca models for stages I and II using  self.batch_size random number of images from the reference dataset
        :param list dir_fnames: List of filenames in the reference sequence
        :param : string dset_name: Name of the dataset
        """
        vgg16_feature_arr = []
        vgg16_feature_geom_arr = []
        n_imgs = len(dir_fnames)  # number of images

        # select random images and no more than batch_size
        if n_imgs > self.batch_size:
            n_imgs = self.batch_size
        ran_fnames = random.sample(dir_fnames, n_imgs)

        # get activations for stages I and II
        for idx, fname in enumerate(ran_fnames):
            if idx % 1 == 0:
                print(idx , fname, "pca: calculating activations...")
                self.textBrowser.append(str('{:<5}  {}  {}'.format(idx, fname, "pca: calculating activations...")) )
                QApplication.processEvents()

            fpath = self.ref_dir + fname

            # prepare image resolutions
            img_data1 = self.prepare_img(fpath, self.image_size1)  # stage I
            img_data2 = self.prepare_img(fpath, self.image_size2)    # stage II

            if self.method == 'NetVLAD':
                pass
            elif self.method == 'VGG16':
                vgg16_feature = self.model1.predict(img_data1)
                vgg16_feature_np = np.array(vgg16_feature)
                vgg16_feature_arr.append(vgg16_feature_np)

            # get activations from layer
            vgg16_feature_geom = self.model2.predict(img_data2)
            vgg16_feature_np_geom = np.array(vgg16_feature_geom)
            vgg16_feature_geom_arr.append(vgg16_feature_np_geom)

        # get features for stage I
        if self.method == 'NetVLAD':
            image_batch, net_out, sess = self.prepare_NetVLAD()
            db_array, im_numbers = self.add_baseline_netvlad(ran_fnames, sess, net_out, image_batch)
        elif self.method == 'VGG16':
            h, w, depth = vgg16_feature_np.shape[1], vgg16_feature_np.shape[2], vgg16_feature_np.shape[3]
            db_array, im_numbers = self.add_baseline_vgg16(ran_fnames, vgg16_feature_arr, h, w)

        db_array = np.asarray(db_array)
        vgg16_feature_geom_arr = np.asarray(vgg16_feature_geom_arr)

        # prepare spatial matching arrays
        side = vgg16_feature_geom_arr.shape[2]

        side_eff = side // 2 - 1
        arr_size = side_eff ** 2

        # side_eff = int(np.ceil(side / 2 - 1))
        # arr_size = side_eff ** 2
        geom_array = np.zeros((len(ran_fnames) * arr_size + 1, 4608))

        cnt_geom_arr = 0
        im_numbers_local = []
        # get features for stage II
        for idx, fname in enumerate(ran_fnames):
            if idx % 1 == 0:
                print(idx, fname, "pca: creating spatial matching features...")
                self.textBrowser.append(str('{:<5}  {}  {}'.format(idx, fname, "pca: creating spatial matching features...")) )
                QApplication.processEvents()

            img_no = self.get_img_no(fname)
            vgg16_feature_np_geom = vgg16_feature_geom_arr[idx]
            filter_sel_geom = pp.normalize(np.moveaxis(vgg16_feature_np_geom[0, :, :, self.filtered_kernels_geom], 0, -1).reshape(side * side, 512), norm='l2', axis=1)
            filter_sel_geom = filter_sel_geom.reshape((side, side, 512))
            hg, wg, depthg = vgg16_feature_np_geom.shape[1], vgg16_feature_np_geom.shape[2], vgg16_feature_np_geom.shape[3]
            cnt = 0
            for cgii in range(self.sblk, hg - self.sblk, 2):  # note that stride is 2
                for cgjj in range(self.sblk, wg - self.sblk, 2):  # note that stride is 2
                    if cnt == arr_size:
                        break
                    center = (cgii, cgjj)
                    block_geom = filter_sel_geom[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]
                    block_descrip_geom = block_geom.reshape((2 * self.sblk + 1) ** 2, depthg).flatten()
                    geom_array[cnt_geom_arr] = block_descrip_geom
                    im_numbers_local.append(img_no)
                    cnt_geom_arr += 1
                    cnt += 1

        # train pca
        pca, pca_geom = self.train_pca(db_array, geom_array, self.ns1, self.ns2)
        return pca, pca_geom, db_array

    def crate_db(self):
        """Create CNN descriptors for stages I and II. Scans a directory of images and stores the CNN representation
        in files vectors.npy (stage I) and vectors_local.npy (stage II)"""

        from joblib import dump, load

        # skip if db already exists
        self.dataset_name = os.path.split(os.path.split(self.reference_folder)[0])[1]
        try:
            f = open('./db/stage1_' + self.dataset_name + '_' + self.imageWidthLineEdit_s1.text() + '_' + self.method + '.npy')
            # f = open('./db/stage1_imgnum_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s1.text() + '_' + self.method + '.out')
            f = open('./db/stage1_imgnum_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s1.text() + '_' + self.method + '.npy')
            self.textBrowser.append('{} '.format("STAGE I: database of descriptors already existed and loaded"))
            try:
                f = open('./db/stage2_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s2.text()  + '.npy')
                # f = open('./db/stage2_imgnum_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s2.text() +  '.out')
                f = open('./db/stage2_imgnum_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s2.text() +  '.npy')
                self.textBrowser.append('{} '.format("STAGE II: database of descriptors already existed and loaded"))
                return 0
            except:
                pass
        except:
            pass


        # extract dataset name
        dset_name = os.path.split(os.path.split(self.ref_dir[:-1])[0])[1]

        # get filenames
        dir_fnames = [d for d in os.listdir(self.ref_dir)]
        dir_fnames.sort()

        # number of batches (batches are required due to limited RAM)
        n_batches = int(np.ceil(len(dir_fnames) / self.batch_size))

        # train and save pca models
        pca, pca_geom, db_array = self.calc_pca(dir_fnames, dset_name)
        if self.method == 'NetVLAD':
             pass
        elif self.method == 'VGG16':
            # dump(pca, 'pca/pca' + '_' + 'stage1.joblib')
            dump(pca, 'pca/pca_stage1_' + self.imageWidthLineEdit_s1.text() + '_VGG16.joblib')

        # dump(pca_geom, 'pca/pca' + '_' + 'stage2.joblib')
        dump(pca_geom, 'pca/pca_stage2_' + self.imageWidthLineEdit_s2.text() + '_VGG16.joblib')

        projection_acc = []
        im_numbers_acc = []
        im_numbers_local_acc = []
        projection_geom_acc = []
        for b in range(n_batches):
            if b == n_batches - 1:
                dirb = dir_fnames[b * self.batch_size: len(dir_fnames)]
            else:
                dirb = dir_fnames[b * self.batch_size: b*self.batch_size + self.batch_size]

            vgg16_feature_arr = []
            vgg16_feature_geom_arr = []
            for idx, fname in enumerate(dirb):
                if idx % 1 == 0:
                    print(idx + b * self.batch_size, fname, "calculating activations...")
                    self.textBrowser.append(str('{:<5}  {}  {}'.format(idx + b * self.batch_size, fname, "calculating activations...")))
                    QApplication.processEvents()

                fpath = self.ref_dir + fname

                # prepare both image resolutions
                img_data1 = self.prepare_img(fpath, self.image_size1)
                img_data2 = self.prepare_img(fpath, self.image_size2)

                if self.method == 'NetVLAD':
                    pass
                elif self.method == 'VGG16':
                    vgg16_feature = self.model1.predict(img_data1)
                    vgg16_feature_np = np.array(vgg16_feature)
                    vgg16_feature_arr.append(vgg16_feature_np)

                vgg16_feature_geom = self.model2.predict(img_data2)
                vgg16_feature_np_geom = np.array(vgg16_feature_geom)
                vgg16_feature_geom_arr.append(vgg16_feature_np_geom)

            if self.method == 'NetVLAD':
                image_batch, net_out, sess = self.prepare_NetVLAD()
                db_array, im_numbers = self.add_baseline_netvlad(dirb, sess, net_out, image_batch)
            elif self.method == 'VGG16':
                h, w, depth = vgg16_feature_np.shape[1], vgg16_feature_np.shape[2], vgg16_feature_np.shape[3]
                db_array, im_numbers = self.add_baseline_vgg16(dirb, vgg16_feature_arr, h, w)
            db_array = np.asarray(db_array)

            # prepare spatial matching arrays
            side = np.asarray(vgg16_feature_geom_arr).shape[2]

            side_eff = side // 2 - 1
            arr_size = side_eff ** 2

            # side_eff = int(np.ceil(side / 2 - 1))
            # arr_size = side_eff**2
            geom_array = np.zeros((len(dirb)*arr_size, 4608))

            cnt_geom_arr = 0
            im_numbers_local = []

            for idx, fname in enumerate(dirb):
                if idx % 1 == 0:
                    print(idx + b * self.batch_size, fname, "creating spatial matching features...")
                    self.textBrowser.append(str('{:<5}  {}  {}'.format(idx + b * self.batch_size, fname, "creating spatial matching features...")))
                    QApplication.processEvents()
                img_no = self.get_img_no(fname)
                vgg16_feature_np_geom = vgg16_feature_geom_arr[idx]

                # normalize along the direction of feature maps
                filter_sel_geom = pp.normalize(np.moveaxis(vgg16_feature_np_geom[0, :, :, self.filtered_kernels_geom], 0, -1).
                                               reshape(side*side, 512),  norm='l2', axis=1)
                filter_sel_geom = filter_sel_geom.reshape((side, side, 512))
                hg, wg, depthg = vgg16_feature_np_geom.shape[1], vgg16_feature_np_geom.shape[2], vgg16_feature_np_geom.shape[3]

                # create  CNN cubes
                cnt = 0
                for cgii in range(self.sblk, hg - self.sblk, 2):
                    for cgjj in range(self.sblk, wg - self.sblk, 2):
                        if cnt == arr_size:
                            break
                        center = (cgii, cgjj)
                        block_geom = filter_sel_geom[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]
                        block_descrip_geom = block_geom.reshape((2 * self.sblk + 1) ** 2, depthg).flatten()
                        geom_array[cnt_geom_arr] = block_descrip_geom
                        im_numbers_local.append(img_no)
                        cnt_geom_arr += 1
                        cnt += 1

            # Perform pca
            if self.method == 'NetVLAD':  # if netvlad, do not pca
                projection = db_array
            elif self.method == 'VGG16':
                projection = pca.transform(db_array)
            projection_geom = pca_geom.transform(geom_array)

            # store batches
            projection_acc.append(projection)
            im_numbers_acc.append(im_numbers)
            projection_geom_acc.append(projection_geom)
            im_numbers_local_acc.append(im_numbers_local)

        # save databases to disk
        np.save('db/stage1_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s1.text() + '_' + self.method, np.vstack(projection_acc).astype('float32'))
        np.save('db/stage1_imgnum_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s1.text() + '_' + self.method, np.hstack(im_numbers_acc))
        np.save('db/stage2_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s2.text(), np.vstack(projection_geom_acc).astype('float32'))
        np.save('db/stage2_imgnum_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s2.text(), np.hstack(im_numbers_local_acc))
        self.textBrowser.append('{} '.format("Database of CNN descriptors created"))
        return 0

    def PrintEvaluation(self, color, index, accuracy, precision, recall, f1, fpath, score, tpi=None, file=None, gt=None):
        """[summary]

        Arguments:
            color {[type]} -- [description]
            index {[type]} -- [description]
            accuracy {[type]} -- [description]
            precision {[type]} -- [description]
            recall {[type]} -- [description]
            f1 {[type]} -- [description]
            fpath {[type]} -- [description]
            score {[type]} -- [description]

        Keyword Arguments:
            file {[type]} -- [description] (default: {None})
        """
        print(color + '{:>4}  {:>8}  {:>8}  {:>8} {:>8}   {:>4} {:>8}  {:>6}  {:>8}'.format(str(index + 1),
                                                                                   "A:" + str(np.round(accuracy * 100, 1)) + "%",       # Accuracy
                                                                                   "P:" + str(np.round(precision * 100, 1)) + "%",      # Precision
                                                                                   "R:" + str(np.round(recall * 100, 1)) + "%",         # Recall
                                                                                   "F1:" + str(np.round(f1, 2)),                        # F1
                                                                                   "Q:" + os.path.splitext(os.path.basename(fpath))[0], # Query image
                                                                                   "Rec:" + str(file),                                  # Recognised image
                                                                                   "S:" + str(np.round(score, 1)) + "%",                # Recognition score
                                                                                   "T" + str(np.round(tpi, 2))))



        if index % 10 == 0:
            self.textBrowser.setTextColor(QtGui.QColor(0, 0, 0))
            self.textBrowser.append('{:*^5s}  {:>12}  {:>12}  {:>10}  {:>4}  {:>8}  {:>8}  {:>10}  {:>8}'.format("Index",
                                                                                   "Accuracy(%)",       # Accuracy
                                                                                   "Precision(%)",      # Precision
                                                                                   "Recall(%)",         # Recall
                                                                                   "F1",                        # F1
                                                                                   "Query" , # Query image
                                                                                   "Guess",                                  # Recognised image
                                                                                   "Score(%)",                # Recognition score
                                                                                   "Lat.(s)" ))


        QApplication.processEvents()

        if color == '\033[91m':
            color = QtGui.QColor(255,0,0)  # red
            rgb_str = 'rgb(255, 0, 0)'
        else:
            color = QtGui.QColor(0,128,0)  # green
            rgb_str = 'rgb(0, 128, 0)'

        self.textBrowser.setTextColor(color)

        # self.textBrowser.append('{:>5}  {:>12}  {:>12}  {:>10}  {:>4}  {:>8}  {:>8}  {:>10}  {:>8}'.format((str(index + 1)).center(5),
        #                                                                            (str(np.round(accuracy * 100, 1)) + "%").center(12),       # Accuracy
        #                                                                            (str(np.round(precision * 100, 1)) + "%").center(12),      # Precision
        #                                                                            (str(np.round(recall * 100, 1)) + "%").center(10),         # Recall
        #                                                                            (str(np.round(f1, 2))).center(6),                        # F1
        #                                                                            (str(int(os.path.splitext(os.path.basename(fpath))[0][5:]))).center(8), # Query image
        #                                                                            (str(file)).center(8),                                  # Recognised image
        #                                                                            (str(np.round(score, 1)) + "%").center(10),                # Recognition score
        #                                                                            (str(np.round(tpi, 2))).center(8)))

        # vis_str = self.image_visualize_all(fpath,file,gt)
        vis_str = os.path.basename(fpath) + '_' + os.path.basename(file) +  '_' + os.path.basename(gt)

        clickable_str = '<html><body>  <a href="http://www.' + vis_str + '"style="text-decoration:none;color:' + rgb_str + '"><pre>' +\
                        '{:>5}  {:>12}  {:>12}  {:>10}  {:>4}  {:>8}  {:>8}  {:>10}  {:>8}'.format((str(index + 1)).center(5),
                                                                                   (str(np.round(accuracy * 100, 1)) + "%").center(12),       # Accuracy
                                                                                   (str(np.round(precision * 100, 1)) + "%").center(12),      # Precision
                                                                                   (str(np.round(recall * 100, 1)) + "%").center(10),         # Recall
                                                                                   (str(np.round(f1, 2))).center(6),                        # F1
                                                                                   (str(int(os.path.splitext(os.path.basename(fpath))[0][5:]))).center(8), # Query image
                                                                                   (str(int(os.path.splitext(os.path.basename(file))[0][5:]))).center(8),                                  # Recognised image
                                                                                   (str(np.round(score, 1)) + "%").center(10),                # Recognition score
                                                                                   (str(np.round(tpi, 2))).center(8)) + \
                        '</pre></a></body></html>'



        # clickable_str = self.textBrowser.setHtml(clickable_str)
        self.textBrowser.append(clickable_str)
        QApplication.processEvents()

    def baseline_vgg16(self, im, filtered_kernels, im_numbers, nbrs0):
        """gets the list of candidates (and distances) from IFDB by comparing CNN cubes of the current query"""

        img_hist = np.zeros(self.no_places, float)  # initialise histogram of distances
        img_hist_rep = np.zeros(self.no_places, int)  # initialise histogram of candidates (places)
        im = cv2.resize(im, self.image_size1, interpolation=cv2.INTER_CUBIC)
        rows, cols, _ = im.shape

        # get activations from CNN pre-trained model
        im = np.expand_dims(im, axis=0)
        im = preprocess_input(im)
        vgg16_feature = self.model1.predict(im)

        h, w, depth = vgg16_feature.shape[1], vgg16_feature.shape[2], vgg16_feature.shape[3]
        filter_sel = np.moveaxis(vgg16_feature[0, :, :, filtered_kernels], 0, -1)

        # count how many cubes are there for current image size and stride
        ncubes = 0
        for cii in range(self.lblk, h - self.lblk, 1):
            for cjj in range(self.lblk, h - self.lblk, 1):
                ncubes += 1

        # randomly select maximum number of cubes
        if ncubes > self.max_ncubes:
            mask = np.random.choice(ncubes, self.max_ncubes, replace=False)
        else:
            mask = np.arange(self.max_ncubes)

        # get array containing the vectors formed concatenating blocks sliding around image
        # # vectorized version  #######################
        # cutmeup = as_strided(filter_sel, shape=(h - 2*self.lblk, h - 2*self.lblk, 512, 2*self.lblk+1, 2*self.lblk+1, 512), strides=2 * filter_sel.strides)[:, :, 0, :, :, :]
        # kk = pp.normalize(cutmeup.reshape(36 * (2 * self.lblk + 1) ** 2 ,  len(filtered_kernels)), norm='l2', axis=1)
        # kk2 = kk.reshape(36 , (2 * self.lblk + 1) ** 2 *  len(filtered_kernels))
        # block_descrip = np.asarray(self.pca.transform(kk2))
        # ####################################

        # loop version
        cnt2 = 0
        block_descrip = []
        for cii in range(self.lblk, h - self.lblk, 1):
            for cjj in range(self.lblk, h - self.lblk, 1):
                if cnt2 not in mask:  # skip blocks not selected in the mask
                    cnt2 += 1
                    continue
                center = (cii, cjj)

                # select CNN cube for current position (center), normalize and concatenate
                block = filter_sel[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                block_descrip.append(pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(filtered_kernels)), norm='l2', axis=1).flatten())
                cnt2 += 1

        # pca dimensionality reduction
        block_descrip = np.asarray(self.pca.transform(block_descrip))

        # query database to get list of candidates
        cnt = 0; cnt2 = 0
        for cii in range(self.lblk, h - self.lblk, 1):
            for cjj in range(self.lblk, h - self.lblk, 1):
                if cnt2 not in mask:
                    cnt2 += 1
                    continue
                # select descriptor and calculate distances to database vectors
                descriptor = block_descrip[cnt]
                distances, indices = nbrs0.kneighbors(descriptor.reshape(1, -1))
                cnt += 1; cnt2 += 1

                for rr in range(self.ncand):  # loop through candidates and accumulate statistics
                    try:
                        file = int(im_numbers[indices[0][rr]])
                    except:
                        print("Warning: could not get candidate number")
                        pass
                    img_hist_rep[file] += 1  # accumulate repetitions
                    img_hist[file] += 1      # accumulate distances

        real_ncand = len(img_hist[img_hist != 0])
        if real_ncand < self.ncand:
            real_ncand = self.ncand

        candidates = np.argsort(-img_hist, axis=0)[:real_ncand]  # best top self.ncand candidates
        cand_dist = -np.sort(-img_hist, axis=0)[:real_ncand]  # best top candidates distances

        return candidates, cand_dist, img_hist

    def baseline_netvlad(self, im, sess, net_out, image_batch, vectors, im_numbers, nbrs0):
        # vectors = loadtxt('vectors.out', comments="#", delimiter=",", unpack=False)
        # im_numbers = loadtxt('image_numbers.out', comments="#", delimiter=",", unpack=False)
        # nbrs0 = NearestNeighbors(n_neighbors=self.ncand, algorithm='brute').fit(vectors)
        start0 = time.time()
        # self.pca_nvlad = load('pca/pca' + str(self.num_dim) + '_' + 'SPED_NetVLAD' + str(10000) + '.joblib')

        if len(glob.glob(self.dirname + '/*.jpg')) != 0:
            filenames = glob.glob(self.dirname + '/*.jpg')
        elif len(glob.glob(self.dirname + '/*.png')) != 0:
            filenames = glob.glob(self.dirname + '/*.png')

        filenames.sort()
        max_hist_avg = 0
        img_hist = np.zeros(self.no_places, float)
        img_hist_rep = np.zeros(self.no_places, int)
        # im = cv2.resize(im, self.image_size1, interpolation=cv2.INTER_CUBIC)
        # im = cv2.resize(im, (448, 448), interpolation=cv2.INTER_CUBIC)
        im = cv2.resize(im, self.image_size1, interpolation=cv2.INTER_CUBIC)
        rows, cols, _ = im.shape
        # rotate frame if necessary and pass it through network
        im = np.expand_dims(im, axis=0)
#        im = preprocess_input(im)
        descriptor = sess.run(net_out, feed_dict={image_batch: im})
        descriptor = np.asarray(descriptor)
        distances, indices = nbrs0.kneighbors(descriptor)

        # q = self.db.query("select place, distance from (select place,  hash <-> cube(ARRAY" +
        #              np.array2string(descriptor, separator=', ') +
        #              ") AS distance from vectors vs ) as x order by distance asc LIMIT 100")

        # if len(q.getresult()) < self.ncand:
        if len(distances[0]) < self.ncand:
            # self.ncand = len(q.getresult())
            self.ncand = len(distances[0])

        for rr in range(self.ncand):  # loop through candidates and accumulate statistics
            file = int(im_numbers[indices[0][rr]])
            img_hist_rep[file] += 1  # repetitions
            img_hist[file] += 1E6 - distances[0][rr]

        candidates = np.argsort(-img_hist, axis=0)[:self.ncand]  # best top self.ncand candidates
        cand_dist = -np.sort(-img_hist, axis=0)[:self.ncand]  # best top candidates distances

        return candidates, cand_dist, img_hist

    def get_hor_offset_patch(self, nbrs_inst, array_geom_current, array_geom_db, nlr):
        # array_geom_db = self.vectors_local[np.where(self.image_numbers_local == hit)]
        # train nearest neighbour
        nbrs = nbrs_inst.fit(array_geom_current)
        distances, indices = nbrs.kneighbors(array_geom_db)
        indices_resh = indices.reshape((self.blocks_per_side, self.blocks_per_side))
        eq_arr = np.zeros((self.blocks_per_side, self.blocks_per_side), bool)
        steer_hist = np.zeros(2 * self.blocks_per_side, int)

        # arange = np.arange(self.spatch ** 2).reshape((self.spatch, self.spatch)) - int((self.spatch ** 2 - 1) / 2)
        arange = np.arange((2 * nlr + 1) ** 2).reshape(((2 * nlr + 1, 2 * nlr + 1))) - int(((2 * nlr + 1) ** 2 - 1) / 2)
        # create array padded on the outside so that locations in near the border of the original array can be dealt with
        # we fill it with a value of -1000 that we know never is going to match
        indices_pad = np.pad(indices_resh, nlr, 'constant', constant_values=-1000)
        for ci in range(nlr, indices_pad.shape[0] - nlr, 1):
            for cj in range(nlr, indices_pad.shape[1] - nlr, 1):
                ind_patch = indices_pad[ci - nlr: ci + nlr + 1, cj - nlr: cj + nlr + 1]
                # eq_arr = (ind_patch == (arange + (indices_pad[ci, cj])))
                # eq_arr[ci, cj] = False
                match_idx = np.unravel_index(indices_resh[ci-nlr, cj-nlr], (self.blocks_per_side, self.blocks_per_side))
                if match_idx[1] - (cj - nlr) >= 0:
                    # steer_hist[self.blocks_per_side + (match_idx[1] - (cj - nlr))] += np.sum(eq_arr)
                    steer_hist[self.blocks_per_side + (match_idx[1] - (cj - nlr))] += np.count_nonzero(ind_patch == (arange + (indices_pad[ci, cj])))
                else:
                    # steer_hist[self.blocks_per_side - (np.abs(match_idx[1] - (cj - nlr)))] += np.sum(eq_arr)
                    steer_hist[self.blocks_per_side - (np.abs(match_idx[1] - (cj - nlr)))] += np.count_nonzero(ind_patch == (arange + (indices_pad[ci, cj])))

        steer = np.argmax(steer_hist) - self.blocks_per_side
        offset = np.round((float(steer)/self.blocks_per_side), 3)

        return offset

    def get_score_patch(self, query_indices,  nlr):
        """
        Gets the spatial matching score when using a patch around anchor points
        :param indices_resh:
        :param bdist0:
        :param nlr: the number of activations from the center of the patch to one edge
        :return: the score
        """
        #  accumulate results of matching
        # eq_arr = np.zeros((self.blocks_per_side, self.blocks_per_side, 2 * nlr + 1, 2 * nlr + 1), bool)

        # start_time2 = time.time()

        acc = 0
        query_indices_mod = np.copy(query_indices)
        for kk in range(1, query_indices.shape[0]):
            query_indices_mod[kk, :] = query_indices[kk, :] + kk * ((1 * query_indices.shape[0]+1))

        # pad array with values that will never match the patch (e.g. -1000)
        query_indices_pad = np.pad(query_indices_mod, (nlr), 'constant', constant_values=-1000)

        cand_indices = np.arange((2 * query_indices.shape[0]+1)**2).reshape((2*query_indices.shape[0]+1, 2*query_indices.shape[0]+1)) \
                       - int(((2*query_indices.shape[0]+1)**2 - 1) / 2)

        candc0 = int(cand_indices.shape[1]/2)
        cand_patch = cand_indices[candc0 - nlr: candc0 + nlr + 1, candc0 - nlr: candc0 + nlr + 1]

        for ci in range(nlr, query_indices_pad.shape[0] - nlr, 1):
            for cj in range(nlr, query_indices_pad.shape[1] - nlr, 1):
                # create patch around each position
                query_patch = query_indices_pad[ci - nlr: ci + nlr + 1, cj - nlr: cj + nlr + 1]
                # acc += (query_patch == cand_patch + (query_indices_pad[ci, cj])).sum()
                acc += np.count_nonzero(query_patch == cand_patch + (query_indices_pad[ci, cj]))

        bdist0 = np.sum(acc)

        # end_time2 = time.time()
        # print(end_time2 - start_time2)

        return bdist0

    def create_query_vectors(self, hg, wg, vectors_query, array_geom_query, arr_size):# loop version
        cnt = 0
        for cgii in range(self.sblk, hg - self.sblk, 2):  # increment of 2 is to reduce complexity by skipping every other location
            for cgjj in range(self.sblk, wg - self.sblk, 2):
                if cnt == arr_size:
                    break
                center = (cgii, cgjj)
                block_geom_query = vectors_query[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]  # [:, :, 1:]
                array_geom_query[cnt] = block_geom_query
                cnt += 1
        array_geom_query = self.pca_geom.transform(array_geom_query.reshape(arr_size, 4608))
        return array_geom_query

    def select_method(self):
        """Select the checked option from the available methods"""

        if self.vggRadioButton.isChecked():
            self.method = 'VGG16'
        elif self.netvladRadioButton.isChecked():
            self.method = 'NetVLAD'

    def create_database(self):
        """Takes the images in the selected reference directory and creates CNN features db for STAGE I and II"""

        from keras.models import Model
        from vgg16_places_356 import VGG16_Places365


        # load pre-trained network model
        model = VGG16_Places365(weights='places', include_top=False)

        use_gpu = self.useGpuCheckBox.checkState()

        # define the models for each stage
        model1_name = 'block5_conv2'
        model2_name = 'block4_conv2'
        model1 = Model(model.input, model.get_layer(model1_name).output)  # stage I
        model2 = Model(model.input, model.get_layer(model2_name).output)  # stage II

        self.model1 = model1
        self.model1_name = model1_name
        self.ref_dir = self.reference_folder + '/'
        self.model2 = model2
        self.model2_name = model2_name
        self.image_size1 = (224, 224)
        self.image_size2 = (416, 416)
        self.num_dim1 = 125
        self.num_dim2 = 100
        self.ns1 = 5000  # number of samples to train pca for stage I
        self.ns2 = 5000  # number of samples to train pca for stage II
        self.lblk = 4
        self.sblk = 1
        self.batch_size = 450  # set value according to RAM resources
        self.filtered_kernels = np.arange(512)
        self.filtered_kernels_geom = np.arange(512)
        self.max_ncubes = 36

        self.refresh_view()
        self.crate_db()

    def warning_win(self, title, message1, message2):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message1)
        msg.setInformativeText(message2)
        msg.setWindowTitle(title)
        msg.exec_()

    def recognise_places(self):
        """performs recognition (stage II) based on the candidates provided by baseline_vgg16 (or baseline_netvlad)"""

        self.reset_controls()
        self.refresh_view()

        start0 = time.time()
        import pathlib
        import yaml
        from keras.models import Model
        from vgg16_places_356 import VGG16_Places365
        from numpy import loadtxt
        from joblib import dump, load


        # load pre-trained network model
        model = VGG16_Places365(weights='places', include_top=False)

        # define the models for each stage
        dirname = self.test_folder + '/'
        # method = 'vgg16'
        model1_name = 'block5_conv2'
        model2_name = 'block4_conv2'
        model1 = Model(model.input, model.get_layer(model1_name).output)  # stage I
        model2 = Model(model.input, model.get_layer(model2_name).output)  # stage II

        # load parameters from config file
        my_path = pathlib.Path(__file__).resolve()
        config_path = my_path.parent / 'config.yaml'
        with open(config_path, 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)

        self.ncand = int(self.candidatesLineEdit.text())
        self.lblk = 4
        # self.lblk = (img_size1 // 16 // 2 - 1) // 2
        self.sblk = 1
        self.model1 = model1
        self.model1_name = model1_name
        self.dirname = dirname
        self.model2 = model2
        self.model2_name = model2_name
        # self.ftol = self.cfg['ftol']
        # self.ftol = int(self.frameTolLineEdit.text())
        self.image_size1 = (int(self.imageWidthLineEdit_s1.text()), int(self.imageHeightLineEdit_s1.text()))
        self.image_size2 = (int(self.imageWidthLineEdit_s2.text()), int(self.imageHeightLineEdit_s2.text()))
        self.max_ncubes = 36       # number of CNN cubes used in stage I
        # self.max_ncubes = 6       # number of CNN cubes used in stage I
        self.cp = 0.4               # experimental frame correlation factor
#        self.npf = 2                # number of previously recognised places considered when exploiting frame correlation
        # self.spatch = 9
        self.spatch = 19
        self.dataset = os.path.split(os.path.split(self.dirname)[00])[1]    # dataset name
        self.dataset_name = os.path.split(os.path.split(self.test_folder)[0])[1]


        # read ground truth from csv file
        try:
            # with open(os.path.split(os.path.split(dirname)[0])[0] + '/GroundTruth.csv') as csv_file:
            with open(self.ground_truth_file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                cnt = 0
                gt = []
                for row in csv_reader:
                    if cnt == 0: cnt = 1
                    else: gt.append(row[0])
                gt = np.asarray(gt)
        except:
            self.warning_win('Warning', 'Ground truth csv file not found', 'Please load file first')
            return 0

        try:
            # vectors = np.load('db/vectors.npy')
            vectors = np.load('db/stage1_' + self.dataset_name + '_' + self.imageWidthLineEdit_s1.text() + '_' + self.method + '.npy')
            nbrs0 = NearestNeighbors(n_neighbors=self.ncand, algorithm='brute').fit(vectors)  # brute  ball_tree  kd_tree  auto

            # im_numbers = loadtxt('db/image_numbers.out', comments="#", delimiter=",", unpack=False)
            # im_numbers = loadtxt('db/stage1_imgnum_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s1.text() + '_' + self.method + '.out',
            #                      comments="#", delimiter=",", unpack=False)
            im_numbers = np.load('db/stage1_imgnum_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s1.text() + '_' + self.method + '.npy')
            self.no_places = int(np.max(im_numbers)) + 1
        except:
            self.warning_win('Warning', 'Database for current settings not found', 'Please load reference dir and create db')
            return 0


        try:
            # self.vectors_local = np.load('db/vectors_local.npy')
            self.vectors_local = np.load('db/stage2_'  + self.dataset_name + '_' + self.imageWidthLineEdit_s2.text()  + '.npy')
            # self.image_numbers_local = loadtxt('db/image_numbers_local.out', comments="#", delimiter=",", unpack=False)
            # self.image_numbers_local = loadtxt('db/stage2_imgnum_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s2.text() + '.out'
            #                                    , comments="#", delimiter=",", unpack=False)
            self.image_numbers_local = np.load('db/stage2_imgnum_' + self.dataset_name + '_'  + self.imageWidthLineEdit_s2.text() + '.npy')
        except:
            self.warning_win('Warning', 'Database for current settings not found', 'Please load reference dir and create db')
            return 0

        if self.method == 'NetVLAD':
            pass
        elif self.method == 'VGG16':
            # self.pca = load('pca/pca' + '_' + 'stage1.joblib')
            self.pca = load('pca/pca_stage1_' + self.imageWidthLineEdit_s1.text() + '_VGG16.joblib')

        self.pca_geom = load('pca/pca_stage2_' + self.imageWidthLineEdit_s2.text() + '_VGG16.joblib')

        if len(glob.glob(self.dirname + '/*.jpg')) != 0:
            filenames = glob.glob(self.dirname + '/*.jpg')
        elif len(glob.glob(self.dirname + '/*.png')) != 0:
            filenames = glob.glob(self.dirname + '/*.png')

        if self.method == 'NetVLAD':
            # prepare NetVLAD model
            image_batch, net_out, sess = self.prepare_NetVLAD()
            K.clear_session()
            vgg16 = VGG16_Places365(weights='places', include_top=False)
            self.model2 = Model(vgg16.input, vgg16.get_layer(self.model2_name).output)


        output = open(self.dataset + "_output.txt", "w")
        if self.cfg['video']['onscreen'] == True:
            self.show_recog()
        video_array = []
        tpcnt = 0  # true positive counter
        fncnt = 0  # false negative counter
        fpcnt = 0  # false positive counter
        filenames.sort()
        score_arr = []
        time_arr = []
        res = []

        npf = self.npf   # number of previous frames considered
        pf_arr = np.zeros((npf, 2))
        for i, fpath in enumerate(filenames):

            # controls
            QApplication.processEvents()
            if self.recognition_paused:
                self.textBrowser.append("Recognition paused")
            while self.recognition_paused:
                time.sleep(0.1)
                QApplication.processEvents()
                if self.recognition_continued:
                    self.reset_controls()
                    self.textBrowser.append("Recognition continued")
                    break
                if self.recognition_stopped:
                    break

            if self.recognition_stopped:
                self.reset_controls()
                self.textBrowser.append("Recognition stopped")
                return 0

            start_imgt = time.time()

            # read  frame
            im = cv2.imread(fpath)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

            filtered_kernels = np.arange(512)
            filtered_kernels_geom = np.arange(512)

            # call method for image filtering
            if self.method == 'NetVLAD':
                candidates, cand_dist, img_hist = self.baseline_netvlad(im, sess, net_out, image_batch, vectors, im_numbers, nbrs0)
            elif self.method == 'VGG16':
                candidates, cand_dist, img_hist = self.baseline_vgg16(im, filtered_kernels, im_numbers, nbrs0)

            # get the query image number from its filename
            self.img_no = self.get_img_no(os.path.splitext(os.path.basename(fpath))[0])

            # get spatial matching vectors for query image
            im = cv2.resize(im, self.image_size2, interpolation=cv2.INTER_CUBIC)
            rows, cols, _ = im.shape
            im = np.expand_dims(im, axis=0)
            im = preprocess_input(im)
            vgg16_feature_geom = self.model2.predict(im)
            vgg16_feature_geom = np.array(vgg16_feature_geom)
            side = vgg16_feature_geom.shape[1]
            side_eff = side // 2 - 1
            arr_size = side_eff ** 2
            vectors_query = pp.normalize(np.moveaxis(vgg16_feature_geom[0, :, :, filtered_kernels_geom], 0, -1).reshape(side * side, 512), norm='l2', axis=1)
            vectors_query = vectors_query.reshape((side, side, 512))
            hg, wg, depthg = vgg16_feature_geom.shape[1], vgg16_feature_geom.shape[2], vgg16_feature_geom.shape[3]

            # declare k-NN model
            nbrs_inst = NearestNeighbors(n_neighbors=1, algorithm='brute')
            scores_hist = np.zeros(self.no_places, float)
            seen_score = 0
            min_dist = np.zeros(self.no_places, float)
            min_dist[min_dist == 0] = 1E6
            self.blocks_per_side = side_eff
            nlr = self.spatch // 2

            # loop over image filtering candidates
            for c in range(0, self.ncand, 1):
            # for c in range(0, self.ncand, 10):
                 cand = candidates[c]
                 array_geom_db = self.vectors_local[np.where(self.image_numbers_local == cand)]

                 if c == 0:  # only need to train nearest neighbour once
                     array_geom_query = np.zeros((arr_size, 3, 3, 512))

                     # get spatially-aware vectors
                     # # vectorized version
                     # cutmeup_geom = as_strided(vectors_query,
                     #                     shape=(hg - 2 * self.sblk, hg - 2 * self.sblk, 512, 2 * self.sblk + 1, 2 * self.sblk + 1, 512),
                     #                     strides=2 * vectors_query.strides)[:, :, 0, :, :, :]
                     # kk = cutmeup_geom[::2, ::2]
                     # # kkg = pp.normalize(cutmeup_geom.reshape((hg - 2 * self.sblk)**2 * (2 * self.sblk + 1) ** 2, len(filtered_kernels)), norm='l2', axis=1)
                     # kkg2 = kk.reshape(((hg - 2 * self.sblk)//2)**2, (2 * self.sblk + 1) ** 2 * len(filtered_kernels))
                     # array_geom_query = np.asarray(self.pca_geom.transform(kkg2))
                     # nbrs = nbrs_inst.fit(array_geom_query)

                     # # loop version
                     # array_geom_query = self.create_query_vectors(hg, wg, vectors_query, array_geom_query, arr_size)

                     # cython version
                     # array_geom_query = create_query_vectors_cython(hg, wg, vectors_query, array_geom_query, self.sblk, arr_size, self.pca_geom)

                     cnt = 0
                     for cgii in range(self.sblk, hg - self.sblk, 2):  # increment of 2 is to reduce complexity by skipping every other location
                         for cgjj in range(self.sblk, wg - self.sblk, 2):
                             if cnt == arr_size:
                                 break
                             center = (cgii, cgjj)
                             block_geom_query = vectors_query[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]  # [:, :, 1:]
                             array_geom_query[cnt] = block_geom_query
                             cnt += 1

                     array_geom_query = self.pca_geom.transform(array_geom_query.reshape(arr_size, 4608))

                     # train nearest neighbour for query
                     nbrs = nbrs_inst.fit(array_geom_query)

                 # for each vector in the query, find the distances and indices of the nearest vectors in the current candidate
                 distances, indices = nbrs.kneighbors(array_geom_db)
                 indices_resh = indices.reshape((self.blocks_per_side, self.blocks_per_side))

                 # get score for current candidate
                 bdist0 = self.get_score_patch(indices_resh, nlr)
                 # Cython version
                 # bdist0 =  get_score_patch(indices_resh, nlr)


                 # exploit frame correlation
                 wcand = 1
                 if i >= npf and npf != 0:
                     fmax = 15
                     accfp = 0
                     max_accfp = 0
                     for kk in range(npf):  # loop over past recognised events
                         if len(pf_arr[:, 1]) == 1 or np.max(pf_arr[:, 1]) == 0:
                             strength = 1
                         else:
                             #  contribution of each past event based on recognition score
                             strength = pf_arr[npf - kk - 1, 1] / np.max(pf_arr[:, 1])

                         #  consider only those candidates within +-fmax distance of the past recogntion being considered
                         if np.abs(cand - (pf_arr[npf-kk-1, 0])) <= fmax:
                             contrib = strength * (self.cp / fmax * (fmax - np.abs(cand - (pf_arr[npf-kk-1, 0]))))
                             accfp += contrib

                             # select the maximum contribution
                             if contrib > max_accfp:
                                 max_accfp = contrib

                     wcand = 1 + max_accfp

                 # weight histogram bin taking past recognitions into account
                 scores_hist[cand] = bdist0 * wcand

                 if i > 10 and i % 10 != 0 and bdist0 * wcand * 100 / 189102. > mean_score + self.ecut * std_score:
                     print(mean_score, c)
                     break

            # select highest bin in  histogram as recognised place
            hit = np.argmax(scores_hist)
            score = np.max(scores_hist)

            # uncomment this to calculate steering (used for teach&play navigation based on VPR)
            # steer = self.get_hor_offset(nbrs_inst, array_geom_query, array_geom_db, 0)
            steer = self.get_hor_offset_patch(nbrs_inst, array_geom_query, array_geom_db, nlr)
#            print(np.round(steer*100, 2), '''%''')

            # keep track of previously recognised events
            if npf != 0:
                for pfcnt in np.arange(npf-1):
                    pf_arr[pfcnt, 0] = pf_arr[pfcnt + 1, 0]  # store recognition frame
                    pf_arr[pfcnt, 1] = pf_arr[pfcnt + 1, 1]  # store recognition score
                pf_arr[npf-1, 0] = int(hit)
                pf_arr[npf-1, 1] = np.round(score, 2)

            score = score * 100 / 189102. #  referred to the score of identical images being compared
            if i % 10 == 0:
                score_arr.append(score)
                mean_score = np.mean(np.asarray(score_arr))
                std_score = np.std(np.asarray(score_arr))
            end_imgt = time.time()
            imgt = np.round((end_imgt - start_imgt), 2)
            time_arr.append(end_imgt - start_imgt)
            # print(imgt, np.round(np.mean(np.asarray(time_arr)), 2), seen_score)

            # visualization
            filenum = int(gt[self.img_no - int(min(im_numbers))])
            com_path = fpath[:-len(os.path.basename(fpath))-5]  # common path for Reference and Live
            ext = os.path.splitext(fpath)[1]  # extension of the files
            recog_file = hit
            if len(filenames) > 9999:
                gt_file = com_path + 'Reference/' + 'image' + "{:05d}".format(filenum) + ext
                recog_file = com_path + 'Reference/' + 'image' + "{:05d}".format(recog_file) + ext  # create path for recognized image
            else:
                gt_file = com_path + 'Reference/' + 'image' + "{:04d}".format(filenum) + ext
                recog_file = com_path + 'Reference/' + 'image' + "{:04d}".format(recog_file) + ext  # create path for recognized image

            self.image_visualize_query(fpath)
            self.image_visualize_reference(gt_file)
            self.image_visualize_output(recog_file)

            accuracy = 0
            precision = 0
            recall = 0

            if hit == -1:  # below recognition threshold (false negative)
                fncnt += 1
                color = '\033[91m'
                if tpcnt > 0:
                    accuracy = tpcnt / float(i + 1)
                    precision = tpcnt / float(tpcnt + fpcnt)
                    recall = tpcnt / float(tpcnt + fncnt)
                    f1 = 2 * precision * recall / (precision + recall)
                    self.PrintEvaluation(color, i, accuracy, precision, recall, f1, fpath, score, np.round(np.mean(np.asarray(time_arr)), 2))
                    output.write(str(i) + "," + fpath + "," + "-1" + "," + str(gt[self.img_no - int(min(im_numbers))]) + "," + str(np.round(score, 5)) + "," + str(float(self.min_thresh)) + "\n")

            elif np.abs(hit - int(gt[self.img_no - int(min(im_numbers))])) <= self.ftol:
                tpcnt += 1
                color = '\033[92m'
                accuracy = tpcnt / float(i + 1)
                precision = tpcnt / float(tpcnt + fpcnt)
                recall = tpcnt / float(tpcnt + fncnt)
                f1 = 2 * precision * recall / (precision + recall)
                self.PrintEvaluation(color, i, accuracy, precision, recall, f1, fpath, score,  np.round(np.mean(np.asarray(time_arr)), 2), file=recog_file, gt=gt_file)
                output.write(str(i) + "," + fpath + "," + str(hit) + "," + str(gt[self.img_no - int(min(im_numbers))]) + "," + str(np.round(score, 5)) + "\n")

            else:  # wrongly recognised (false positive)
                fpcnt += 1
                color = '\033[91m'
                if tpcnt > 0:
                    accuracy = tpcnt / float(i + 1)
                    precision = tpcnt / float(tpcnt + fpcnt)
                    recall = tpcnt / float(tpcnt + fncnt)
                    f1 = 2 * precision * recall / (precision + recall)
                    self.PrintEvaluation(color, i, accuracy, precision, recall, f1, fpath, score, np.round(np.mean(np.asarray(time_arr)), 2), file=recog_file, gt=gt_file)
                    output.write(str(i) + "," +  fpath + "," + str(hit) + "," + str(gt[self.img_no - int(min(im_numbers))]) + "," + str(np.round(score, 5)) + "\n")

            # # initialize plots for results pictures
            if self.cfg['video']['onscreen'] == True:

                # # show result images
                self.vis = self.plot_res_pics(fpath, hit, im_numbers, gt[self.img_no - int(min(im_numbers))])
                self.vis = cv2.resize(self.vis, (1440, 480))
                video_array.append(self.vis)
                # cv2.waitKey(0)
            res.append((str(i), hit))
        output.close()

        if self.cfg['video']['onscreen'] == True:
            out = cv2.VideoWriter('project.mp4', cv2.VideoWriter_fourcc(*'H264'), 1.0, (self.vis.shape[1], self.vis.shape[0]))
            for i in range(len(video_array)):
                out.write(video_array[i])
            out.release()
        end0 = time.time()

        color = QtGui.QColor(0,0,0)  # black
        self.textBrowser.setTextColor(color)
        self.textBrowser.append("Recognition finished")
        return accuracy, precision, recall, end0 - start0, np.round(np.mean(np.asarray(time_arr)), 2)



