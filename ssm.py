import cv2
import ssmbase
import glob
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThreadPool, QRunnable
from sklearn.decomposition import PCA
import sklearn.preprocessing as pp
from sklearn.neighbors import NearestNeighbors
import random
import csv
import time
import about
import os
import numpy as np
import tkinter
from tkinter import filedialog, Tk, messagebox
from shutil import copyfile
from matplotlib import pyplot as plt
import torch
import torchvision.models as models
from torchvision import transforms as T
from PIL import Image
from sklearn.feature_extraction import image
import netvlad_model
import skimage.measure

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

print ("OpenCV v" + cv2.__version__)

class ssm_MainWindow(ssmbase.Ui_MainWindow):
    """ """
    def setupUi(self, MainWindow):
        """ Sets up the VPR user interface  default parameters."""
        ssmbase.Ui_MainWindow.setupUi(self, MainWindow)

        self.threadpool = QThreadPool()
        # print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.method1 = 'VGG16'
        self.method2 = 'VGG16'


        self.reference_folder = str()
        self.test_folder = str()
        self.ground_truth_file = str()
        self.recognition_paused = False
        self.recognition_continued = False
        self.recognition_stopped = False

        self.useGpuCheckBox.setChecked(1)
        self.useGpuCheckBox.setToolTip('Enables/disables the use of GPU')
        self.loadDbOnGpuCheckBox.setChecked(1)
        self.loadDbOnGpuCheckBox.setToolTip('If enough GPU memory is available, enabling this feature speeds up recognition.')
        self.gpuCandLineEdit.setToolTip('Maximum number of candidates loaded on GPU at a time.'
                                        ' Please use a fraction of the total number of candidates to reduce GPU memory requirements')

        self.actionAbout.triggered.connect(self.showAboutBox)

        self.textBrowser.append("OpenCV v" + cv2.__version__)
        self.path = None
        # self.actionSave_path.triggered.connect(self.savePath)
        self.stopSignal = False

        # stage I
        self.imageWidthLineEdit_s1.textChanged.connect(self.refresh_view)
        self.imageWidthLineEdit_s2.textChanged.connect(self.refresh_view)
        # self.imageWidthLineEdit_s1.returnPressed.connect(self.refresh_view)
        # self.imageHeightLineEdit_s1.returnPressed.connect(self.refresh_view)
        self.vggRadioButton.setDisabled(0)
        self.vggRadioButton.click()
        self.netvladRadioButton.setDisabled(0)
        self.vggRadioButton.toggled.connect(self.refresh_view)
        self.vggRadioButton.setToolTip('Uses the VGG16 architecture trained from scratch on the Places365 dataset.'
                                          ' Based on experiments, descriptors are created from the activations of layer'
                                          ' "conv5_2".')
        self.netvladRadioButton.toggled.connect(self.refresh_view)
        self.netvladRadioButton.setToolTip('Uses NetVLAD architecture trained on the Pittsburg 30k dataset.')
        self.resnetRadioButton.toggled.connect(self.refresh_view)
        self.resnetRadioButton.setToolTip('Uses ResNet-152 architecture trained from scratch on the Places365 dataset.'
                                          ' Based on experiments, descriptors are created from the activations of layer'
                                          ' "SpatialConvolution_121".')
        self.googlenetRadioButton.toggled.connect(self.refresh_view)
        self.googlenetRadioButton.setToolTip('Uses GoogLeNet architecture trained from scratch on the Places365 dataset.'
                                             ' Based on experiments, descriptors are created from the activations of layer'
                                             ' "inception_3a_output" ')

        self.pcaDimLineEdit_s1.setToolTip('Number of PCA components during compression')
        self.pcaDimLineEdit_s1.textChanged.connect(self.refresh_view)
        self.pcaSamplesLineEdit_s1.setToolTip('Number of samples extracted from reference images and used to train PCA')
        self.pcaSamplesLineEdit_s1.textChanged.connect(self.refresh_view)



        # stage II
        self.imageWidthLineEdit_s2.returnPressed.connect(self.refresh_view)
        self.imageHeightLineEdit_s2.returnPressed.connect(self.refresh_view)

        self.vggRadioButton_s2.setDisabled(0)
        self.vggRadioButton_s2.click()
        self.imageSizeGroupBox_s1.setEnabled(False)
        self.vggRadioButton_s2.toggled.connect(self.refresh_view)
        self.vggRadioButton_s2.setToolTip('Uses the VGG16 architecture trained from scratch on the Places365 dataset.'
                                          ' Based on experiments, descriptors are created from the activations of layer'
                                          ' "conv4_2".')
        self.resnetRadioButton_s2.toggled.connect(self.refresh_view)
        self.resnetRadioButton_s2.setToolTip('Uses ResNet-152 architecture trained from scratch on the Places365 dataset.'
                                          ' Based on experiments, descriptors are created from the activations of layer'
                                          ' "to be determined".')
        self.googlenetRadioButton_s2.toggled.connect(self.refresh_view)
        self.googlenetRadioButton_s2.setToolTip('Uses GoogLeNet architecture trained from scratch on the Places365 dataset.'
                                             ' Based on experiments, descriptors are created from the activations of layer'
                                             ' "to be determined" ')


        self.candidatesLineEdit.setToolTip('Number of candidates  selected in STAGE I (use 1 to consider that stage only')
        self.candidatesLineEdit.returnPressed.connect(self.refresh_view)

        self.frameTolLineEdit.setToolTip('Number of frames (\u00B1) that are considered as belonging to the same place')
        self.frameTolLineEdit.returnPressed.connect(self.refresh_view)

        # self.earlyCutLineEdit.setToolTip('Adds (>0) or subtracts (<0) to the average recognition score, setting the threshold for early cut of candidates. Units are in standard deviations of the score.')
        # self.earlyCutLineEdit.returnPressed.connect(self.refresh_view)

        self.prevFramesLineEdit.setToolTip('Number of frames previous to current recognition used to improve recognition (use 0 to disable frame correlation)')
        self.prevFramesLineEdit.returnPressed.connect(self.refresh_view)

        self.pcaDimLineEdit_s2.setToolTip('Number of PCA components during compression')
        self.pcaDimLineEdit_s2.textChanged.connect(self.refresh_view)
        self.pcaSamplesLineEdit_s2.setToolTip('Number of samples extracted from reference images and used to train PCA')
        self.pcaSamplesLineEdit_s2.textChanged.connect(self.refresh_view)

        # select files
        self.btnLoadReference.clicked.connect(self.search_for_dir_path_reference)
        self.btnLoadTest.clicked.connect(self.search_for_dir_path_query)
        self.btnLoadGroungTruth.clicked.connect(self.search_for_file_path_ground_truth)

        ## hardcoded for quick testing
        #self.reference_folder = "/data/Datasets/Kudamm_icra/Reference"
        #self.refOkLabel.setText(self.reference_folder)
        #self.test_folder = "/data/Datasets/Kudamm_icra/Live"
        #self.testOkLabel.setText(self.test_folder)
        #self.ground_truth_file = os.path.dirname(self.test_folder) + '/GroundTruth.csv'
        #self.groundTruthOkLabel.setText(self.ground_truth_file)

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

        # worker = Plot_PR_curves(self.frameTolLineEdit.text())
        # self.threadpool.start(worker)
        # self.btnPRcurves.clicked.connect(self.plot_PR_curves)
        self.btnPRcurves.clicked.connect(self.set_plot_thread)

        # gpu
        self.useGpuCheckBox.clicked.connect(self.use_gpu)
        self.loadDbOnGpuCheckBox.clicked.connect(self.use_gpu)
        self.gpuCandLineEdit.setText(str(int(self.candidatesLineEdit.text()) // 10))
        self.gpuCandLineEdit.textChanged.connect(self.refresh_view)


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
            # make image sizes square
            self.imageHeightLineEdit_s1.setText(self.imageWidthLineEdit_s1.text())
            self.imageHeightLineEdit_s2.setText(self.imageWidthLineEdit_s2.text())

            self.image_size1 = (int(self.imageWidthLineEdit_s1.text()), int(self.imageHeightLineEdit_s1.text()))
            self.image_size2 = (int(self.imageWidthLineEdit_s2.text()), int(self.imageHeightLineEdit_s2.text()))

            # method
            self.select_method_stage1()
            self.select_method_stage2()


            # paramaters
            self.ncand = int(self.candidatesLineEdit.text())
            self.ftol = int(self.frameTolLineEdit.text())
            self.npf = int(self.prevFramesLineEdit.text())
            # self.ecut = float(self.earlyCutLineEdit.text())

            # PCA
            self.num_dim1 = int(self.pcaDimLineEdit_s1.text())
            self.num_dim2 = int(self.pcaDimLineEdit_s2.text())
            self.ns1 = int(self.pcaSamplesLineEdit_s1.text())
            self.ns2 = int(self.pcaSamplesLineEdit_s2.text())

            # GPU
            self.gpu_max_candidates = int(self.gpuCandLineEdit.text())

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
        # import tkinter
        # from tkinter import filedialog, Tk
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
        # import tkinter
        # from tkinter import filedialog, Tk
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

        try:
            f = open(os.path.dirname(self.test_folder) + '/GroundTruth.csv')
            self.ground_truth_file = os.path.dirname(self.test_folder) + '/GroundTruth.csv'
            self.groundTruthOkLabel.setText(self.ground_truth_file)
        except:
            pass

    def search_for_file_path_ground_truth(self):

        # initiate tinker and hide window
        main_win = tkinter.Tk()
        main_win.withdraw()

        # open file selector
        self.ground_truth_file = filedialog.askopenfilename(parent=main_win, initialdir="/", title='Please select a file')

        # close window after selection
        main_win.destroy()

        if len(self.ground_truth_file) != 0:
            # self.groundTruthOkLabel.setText(u'\u2713')
            self.groundTruthOkLabel.setText(self.ground_truth_file)
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
        options['initialfile'] = (self.dataset_name + '_' +  self.method1 + '_' +  self.method2 + '-'   # image retrieval method (stage I) \
                                 + str(self.image_size1[0]) + '_'               # stage I image size \
                                 + str(self.image_size2[0]) + '_'               # stage II image size \
                                 + str(self.candidatesLineEdit.text()) + '_'    # number of candidates \
                                 + str(self.frameTolLineEdit.text()) + '_'      # frame tolerance \
                                 + str(self.prevFramesLineEdit.text())     )     # number of previous frames considered in FC
        options['title'] = 'Save default output filename'
        filename = filedialog.asksaveasfile(mode='w', **options)
        copyfile('Live_output.txt', filename.name)

    def set_plot_thread(self):
        if len(plt.get_fignums()) == 0:
            root = Tk()
            # self.thread_on = 1
            self.pr_file = filedialog.askopenfilenames(initialdir="output", title='Please select results file. You can select more than one')
            worker = Plot_PR_curves(self.frameTolLineEdit.text(), self.pr_file)
            self.threadpool.start(worker)
            root.withdraw()
        else:
            self.warning_win('Warning', 'A figure is currently being displayed.', 'Please, close it first.')
            # return 0

    # def use_gpu(self):
    #     if self.useGpuCheckBox.checkState() == 0:
    #         os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    #         os.environ["CUDA_VISIBLE_DEVICES"] = ""
    #     else:
    #         pass

    def use_gpu(self):
        if not self.useGpuCheckBox.isChecked():
            self.gpuGroupBox.setEnabled(False)
        else:
            self.gpuGroupBox.setEnabled(True)
            self.refresh_view()



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

    def get_stage1_vgg16_descrip(self, fnames,  all_activ_arr):
        """
        Creates VGG16 descriptors (trained on Places365 dataset) for Stage I of the system

        Parameters
        ----------
        fnames          : List of file names to create features from
        vgg16_activ_arr : Array of activations
        h               : Feature map height
        w               : Feature map width

        Returns
        -------
        descrip_array   : Array of descriptors for all images
        im_numbers      : Array of image identifiers
        """

        h, w, depth = all_activ_arr[0].shape[1], all_activ_arr[0].shape[2], all_activ_arr[0].shape[3]
        self.channels = np.arange(depth)
        descrip_array = []
        im_numbers = []
        max_ncubes = self.max_ncubes
        for idx, fname in enumerate(fnames):
            img_activ_arr = all_activ_arr[idx]
            img_activ_arr = np.moveaxis(img_activ_arr[0, :, :, self.channels], 0, -1)

            # count how many cubes there are for current image size
            ncubes = 0
            for cii in range(self.lblk, h - self.lblk, 1):
                for cjj in range(self.lblk, w - self.lblk, 1):
                    ncubes += 1

            # reduce the number of cubes if required
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
                    block = img_activ_arr[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                    block_descrip = pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.channels)), norm='l2', axis=1).flatten()
                    descrip_array.append(block_descrip)
                    img_no = self.get_img_no(fname)
                    im_numbers.append(img_no)
                    cnt2 += 1
        print(ncubes, " cubes where created per image")
        self.textBrowser.append(str('{}  {}'.format(ncubes,  " cubes where created per image")))

        return descrip_array, im_numbers

    def get_stage1_resnet_descrip(self, fnames,  all_activ_arr):
        """
        Creates ResNet-152 descriptors (trained on Places365 dataset) for Stage I of the system

        Parameters
        ----------
        fnames          : List of file names to create features from
        vgg16_activ_arr : Array of activations
        h               : Feature map height
        w               : Feature map width

        Returns
        -------
        descrip_array   : Array of descriptors for all images
        im_numbers      : Array of image identifiers
        """

        h, w, depth = all_activ_arr[0].shape[1], all_activ_arr[0].shape[2], all_activ_arr[0].shape[3]
        self.channels = np.arange(depth)
        descrip_array = []
        im_numbers = []
        max_ncubes = self.max_ncubes
        for idx, fname in enumerate(fnames):
            img_activ_arr = all_activ_arr[idx]
            img_activ_arr = np.moveaxis(img_activ_arr[0, :, :, self.channels], 0, -1)

            # count how many cubes there are for current image size
            ncubes = 0
            for cii in range(self.lblk, h - self.lblk, 1):
                for cjj in range(self.lblk, w - self.lblk, 1):
                    ncubes += 1

            # reduce the number of cubes if required
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
                    block = img_activ_arr[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                    block_descrip = pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.channels)), norm='l2', axis=1).flatten()
                    descrip_array.append(block_descrip)
                    img_no = self.get_img_no(fname)
                    im_numbers.append(img_no)
                    cnt2 += 1
        print(ncubes, " cubes where created per image")
        self.textBrowser.append(str('{}  {}'.format(ncubes,  " cubes where created per image")))

        return descrip_array, im_numbers

    def get_stage1_googlenet_descrip(self, fnames,  all_activ_arr):
        """
        Creates GoogLeNet descriptors (trained on Places365 dataset) for Stage I of the system

        Parameters
        ----------
        fnames          : List of file names to create features from
        vgg16_activ_arr : Array of activations
        h               : Feature map height
        w               : Feature map width

        Returns
        -------
        descrip_array   : Array of descriptors for all images
        im_numbers      : Array of image identifiers
        """

        h, w, depth = all_activ_arr[0].shape[1], all_activ_arr[0].shape[2], all_activ_arr[0].shape[3]
        self.channels = np.arange(depth)
        descrip_array = []
        im_numbers = []
        max_ncubes = self.max_ncubes
        for idx, fname in enumerate(fnames):
            img_activ_arr = all_activ_arr[idx]
            img_activ_arr = np.moveaxis(img_activ_arr[0, :, :, self.channels], 0, -1)

            # count how many cubes there are for current image size
            ncubes = 0
            for cii in range(self.lblk, h - self.lblk, 1):
                for cjj in range(self.lblk, w - self.lblk, 1):
                    ncubes += 1

            # reduce the number of cubes if required
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
                    block = img_activ_arr[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                    block_descrip = pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.channels)), norm='l2', axis=1).flatten()
                    descrip_array.append(block_descrip)
                    img_no = self.get_img_no(fname)
                    im_numbers.append(img_no)
                    cnt2 += 1
        print(ncubes, " cubes where created per image")
        self.textBrowser.append(str('{}  {}'.format(ncubes,  " cubes where created per image")))

        return descrip_array, im_numbers

    def get_img_no(self, fname):
        """gets the right image number from image filename"""
        img_no = int(''.join(map(str, [int(s) for s in os.path.splitext(fname)[0] if s.isdigit()])))
        return img_no

    def train_pca(self, db_array, geom_array, ns1, ns2, netvlad_ns1):
        """
        Trains PAC models for  stages I and II
        :param db_array: Vectors for stage I
        :param geom_array: Vectors for stage II
        :param ns1: Max number of samples for stage I
        :param ns2: Max number of samples for stage II
        :return pca, pca_geom: pca models
        """

        print("training PCA...")
        self.textBrowser.append(str('{}'.format("training PCA...")))
        QApplication.processEvents()
        pca = None
        if ns2 > len(geom_array):
            ns2 = len(geom_array)

        if len(db_array) > ns1:
            if self.method1 == 'NetVLAD':
                pass
                # if netvlad_ns1 > 4096: netvlad_ns1 = 4096
                # mask = np.random.choice([False, True], len(db_array), p=[1 - ns1 / len(db_array), ns1 / len(db_array)])
                # pca = PCA(n_components=netvlad_ns1, svd_solver='full', whiten=True).fit(db_array[np.where(mask == True)])

            elif self.method1 == 'VGG16':
                # select samples randomly for stage I
                mask = np.random.choice([False, True], len(db_array), p=[1 - ns1 / len(db_array), ns1 / len(db_array)])
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array[np.where(mask ==True)])
            elif self.method1 == 'ResNet':
                # select samples randomly for stage I
                mask = np.random.choice([False, True], len(db_array), p=[1 - ns1 / len(db_array), ns1 / len(db_array)])
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array[np.where(mask ==True)])
            elif self.method1 == 'GoogLeNet':
                # select samples randomly for stage I
                mask = np.random.choice([False, True], len(db_array), p=[1 - ns1 / len(db_array), ns1 / len(db_array)])
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array[np.where(mask ==True)])

            # select samples randomly for stage II
            mask_geom = np.random.choice([False, True], len(geom_array), p=[1 - ns2 / len(geom_array), ns2 / len(geom_array)])
            pca_geom = PCA(n_components=self.num_dim2, svd_solver='full', whiten=True).fit(geom_array[np.where(mask_geom == True)])
        else:
            if self.method1 == 'NetVLAD':
                pass
                # if netvlad_ns1 > 4096: netvlad_ns1 = 4096
                # pca = PCA(n_components=netvlad_ns1, svd_solver='full', whiten=True).fit(db_array)
            elif self.method1 == 'VGG16':
                # perform pca on all samples
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array)
            elif self.method1 == 'ResNet':
                # perform pca on all samples
                pca = PCA(n_components=self.num_dim1, svd_solver='full', whiten=True).fit(db_array)
            elif self.method1 == 'GoogLeNet':
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

    def forward1(self, x, conv4_2, conv5_2):
        results = []
        for ii, model in enumerate(self.model1_pt):
            x = model(x)
            if ii in {conv4_2, conv5_2}:
                results.append(x)
                if ii == conv5_2:
                    break
        return results

    def forward2(self, x, conv4_2, conv5_2):
        results = []
        for ii, model in enumerate(self.model2_pt):
            x = model(x)
            if ii in {conv4_2, conv5_2}:
                results.append(x)
                if ii == conv5_2:
                    break
        return results

    def create_base_and_netvlad_models(self):
        base_model_dim = 512
        num_clusters = 64
        vladv2 = True
        base_model = models.vgg16(pretrained=True)

        # capture only feature part and remove last relu and maxpool
        layers = list(base_model.features.children())[:-2]

        # only train conv5_1, conv5_2, and conv5_3
        for l in layers[:-5]:
            for p in l.parameters():
                p.requires_grad = False

        base_model = torch.nn.Sequential(*layers)
        net_vlad = netvlad_model.NetVLAD(num_clusters=num_clusters, dim=base_model_dim, vladv2=vladv2)

        return base_model, net_vlad


    def calc_pca(self, dir_fnames):
        """
        Calculates the pca models for stages I and II using  self.batch_size random number of images from the reference dataset

        Parameters
        ----------
        dir_fnames: List of file names in the reference sequence

        Returns
        -------
        stage1_pca, stage2_pca : PCA models for both stages

        """

        stage1_activ_arr = []
        stage2_activ_arr = []
        im_numbers_netvlad = []
        n_imgs = len(dir_fnames)  # number of images

        # select random images and no more than batch_size
        if n_imgs > self.batch_size:
            n_imgs = self.batch_size
        ran_fnames = random.sample(dir_fnames, n_imgs)

        # get activations for stages I and II
        for idx, fname in enumerate(ran_fnames):
            if idx % 1 == 0:
                print(idx , fname, "PCA: calculating activations...")
                self.textBrowser.append(str('{:<5}  {}  {}'.format(idx, fname, "PCA: calculating activations...")) )
                QApplication.processEvents()

            fpath = self.ref_dir + fname
            img_no = self.get_img_no(fname)
            im_numbers_netvlad.append(img_no)

            # get and store activations
            stage1_activ, stage2_activ = self.get_pytorch_tensors(fpath)

            # maxpool the layer to make it compatible with code
            if self.method1 != 'NetVLAD':
                if stage1_activ.shape[1] > 14:
                    red_factor = stage1_activ.shape[1] // 14
                    stage1_activ = skimage.measure.block_reduce(stage1_activ, (1, red_factor, red_factor, 1), np.max)
                elif stage1_activ.shape[1] < 14:
                    # TODO upsample array to make it compatible with size 14x14
                    pass

            stage1_activ_arr.append(stage1_activ)
            stage2_activ_arr.append(stage2_activ)

        # get features for stage I
        if self.method1 == 'VGG16':
            stage1_descrip_arr, im_numbers = self.get_stage1_vgg16_descrip(ran_fnames, stage1_activ_arr)
        elif self.method1 == 'NetVLAD':
            stage1_descrip_arr = np.squeeze(stage1_activ_arr, axis=1)
        elif self.method1 == 'ResNet':
            stage1_descrip_arr, im_numbers = self.get_stage1_resnet_descrip(ran_fnames, stage1_activ_arr)
        elif self.method1 == 'GoogLeNet':
            stage1_descrip_arr, im_numbers = self.get_stage1_googlenet_descrip(ran_fnames, stage1_activ_arr)

        stage1_descrip_arr = np.asarray(stage1_descrip_arr)

        # prepare spatial matching arrays
        stage2_activ_arr = np.asarray(stage2_activ_arr)
        side = stage2_activ_arr.shape[2]
        side_eff = side - 2 * self.sblk
        arr_size = side_eff ** 2

        stage2_descrip_arr = np.zeros((len(ran_fnames) * arr_size + 1, 3 * 3 * stage2_activ_arr.shape[4]))
        hg, wg, depthg = stage2_activ_arr.shape[2], stage2_activ_arr.shape[3], stage2_activ_arr.shape[4]
        self.channels_geom = np.arange(depthg)

        cnt_geom_arr = 0
        im_numbers_local = []
        # get features for stage II
        for idx, fname in enumerate(ran_fnames):
            if idx % 1 == 0:
                print(idx, fname, "PCA: creating spatial matching features...")
                self.textBrowser.append(str('{:<5}  {}  {}'.format(idx, fname, "PCA: creating spatial matching features...")) )
                QApplication.processEvents()

            img_no = self.get_img_no(fname)
            stage2_activ = stage2_activ_arr[idx]
            filter_sel_geom = pp.normalize(np.moveaxis(stage2_activ[0, :, :, self.channels_geom], 0, -1).reshape(side * side, depthg), norm='l2', axis=1)
            filter_sel_geom = filter_sel_geom.reshape((side, side, depthg))
            cnt = 0
            for cgii in range(self.sblk, hg - self.sblk, 1):  # note that stride is 2
                for cgjj in range(self.sblk, wg - self.sblk, 1):  # note that stride is 2
                    if cnt == arr_size:
                        break
                    center = (cgii, cgjj)
                    block_geom = filter_sel_geom[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]
                    block_descrip_geom = block_geom.reshape((2 * self.sblk + 1) ** 2, depthg).flatten()
                    stage2_descrip_arr[cnt_geom_arr] = block_descrip_geom
                    im_numbers_local.append(img_no)
                    cnt_geom_arr += 1
                    cnt += 1

        # train pca
        stage1_pca, stage2_pca = self.train_pca(stage1_descrip_arr, stage2_descrip_arr, self.ns1, self.ns2, len(ran_fnames) )

        return stage1_pca, stage2_pca

    def get_pytorch_tensors(self, fpath):
        """
        Get pytorch tensors for selected layers in the network

        Parameters
        ----------
        fpath: path to file

        Returns: activation tensors for stage I and II
        -------

        """

        input_image = Image.open(fpath)
        input_tensor1 = self.preprocess1(input_image)
        input_tensor2 = self.preprocess2(input_image)
        input_batch1 = input_tensor1.unsqueeze(0)
        input_batch2 = input_tensor2.unsqueeze(0)

        # move the input and model to GPU for speed if available
        if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
            input_batch1 = input_batch1.to('cuda')
            input_batch2 = input_batch2.to('cuda')

        # results1 = self.forward1(input_batch1, 19, 26)  # conv_4-2 and conv_5-2
        # results2 = self.forward2(input_batch2, 19, 26)  # conv_4-2 and conv_5-2        #
        with torch.no_grad():
            results1 = self.model_stage1.forward1(input_batch1)  # one feature per image
            if self.method1 == 'NetVLAD':
                stage1_activ = results1.cpu().numpy()
            else:
                stage1_activ = results1.permute(0, 2, 3, 1).cpu().numpy()

            results2 = self.model_stage2.forward2(input_batch2)  # forward2 defined in the model class
            stage2_activ = results2.permute(0, 2, 3, 1).cpu().numpy()

            # if self.method == 'VGG16':
            #     results1 = self.model_vgg16.forward1(input_batch1)  # forward1 defined in the model class
            #     results2 = self.model_vgg16.forward2(input_batch2)  # forward2 defined in the model class
            #     stage1_activ = results1.permute(0, 2, 3, 1).cpu().numpy()
            #     stage2_activ = results2.permute(0, 2, 3, 1).cpu().numpy()
            # elif self.method == 'NetVLAD':
            #     results1 = self.model_netvlad.forward(input_batch1)  # one feature per image
            #     results2 = self.model_vgg16.forward2(input_batch2)  # forward2 defined in the model class
            #     stage1_activ = results1.cpu().numpy()
            #     stage2_activ = results2.permute(0, 2, 3, 1).cpu().numpy()
            # elif self.method == 'ResNet':
            #     results1 = self.model_resnet.forward1(input_batch1)  # forward1 defined in the model class
            #     results2 = self.model_vgg16.forward2(input_batch2)  # forward2 defined in the model class
            #     stage1_activ = results1.permute(0, 2, 3, 1).cpu().numpy()
            #     stage2_activ = results2.permute(0, 2, 3, 1).cpu().numpy()
            # elif self.method == 'GoogLeNet':
            #     results1 = self.model_googlenet.forward1(input_batch1)  # forward1 defined in the model class
            #     results2 = self.model_vgg16.forward2(input_batch2)  # forward2 defined in the model class
            #     stage1_activ = results1.permute(0, 2, 3, 1).cpu().numpy()
            #     stage2_activ = results2.permute(0, 2, 3, 1).cpu().numpy()

        del input_batch1
        del input_batch2

        return stage1_activ, stage2_activ

    def create_db(self):
        """Create CNN descriptors for stages I and II. Scans a directory of images and stores the CNN representation
        in files vectors.npy (stage I) and vectors_local.npy (stage II)"""

        from joblib import dump, load

        # skip if db already exists
        self.dataset_name = os.path.split(os.path.split(self.reference_folder)[0])[1]
        try:
            f = open('./db/' + self.dataset_name + '_stage1_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1 + '.npy')
            f = open('./db/' + self.dataset_name + '_stage1_imgnum_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1 + '.npy')
            self.textBrowser.append('{} '.format("STAGE I: database of descriptors already existed and loaded"))
            try:
                f = open('./db/'  + self.dataset_name + '_stage2_' + self.imageWidthLineEdit_s2.text()  + '_' + self.method2 + '.npy')
                f = open('./db/'  + self.dataset_name + '_stage2_imgnum_' + self.imageWidthLineEdit_s2.text() + '_' + self.method2 +  '.npy')
                self.textBrowser.append('{} '.format("STAGE II: database of descriptors already existed and loaded"))
                return 0
            except:
                pass
        except:
            pass

        # # extract dataset name
        # dset_name = os.path.split(os.path.split(self.ref_dir[:-1])[0])[1]

        # get filenames
        dir_fnames = [d for d in os.listdir(self.ref_dir)]
        dir_fnames.sort()

        # number of batches (batches are required due to limited RAM, nothing to do with CNN batches)
        n_batches = int(np.ceil(len(dir_fnames) / self.batch_size))

        # train and save pca models
        pca, pca_geom = self.calc_pca(dir_fnames)

        if self.method1 == 'NetVLAD':
            pass
            # dump(pca, 'pca/pca_stage1_' + self.imageWidthLineEdit_s1.text() + '_NetVLAD.joblib')
        else:
            dump(pca, 'pca/pca_stage1_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1 + '.joblib')

        dump(pca_geom, 'pca/pca_stage2_' + self.imageWidthLineEdit_s2.text() + '_' + self.method2 + '.joblib')


        stage1_projection_acc = []
        im_numbers_acc = []
        stage2_projection_acc = []
        im_numbers_local_acc = []
        for b in range(n_batches):
            if b == n_batches - 1:
                dirb = dir_fnames[b * self.batch_size: len(dir_fnames)]
            else:
                dirb = dir_fnames[b * self.batch_size: b*self.batch_size + self.batch_size]

            stage1_activ_arr = []
            stage2_activ_arr = []
            im_numbers_netvlad = []
            for idx, fname in enumerate(dirb):
                if idx % 1 == 0:
                    print(idx + b * self.batch_size, fname, "calculating activations...")
                    self.textBrowser.append(str('{:<5}  {}  {}'.format(idx + b * self.batch_size, fname, "calculating activations...")))
                    QApplication.processEvents()

                fpath = self.ref_dir + fname
                img_no = self.get_img_no(fname)
                im_numbers_netvlad.append(img_no)

                stage1_activ, stage2_activ = self.get_pytorch_tensors(fpath)

                # maxpool the layer to make it compatible with code
                if self.method1 != 'NetVLAD':
                    if stage1_activ.shape[1] > 14:
                        red_factor = stage1_activ.shape[1] // 14
                        stage1_activ = skimage.measure.block_reduce(stage1_activ, (1, red_factor, red_factor, 1), np.max)
                    elif stage1_activ.shape[1] < 14:
                        # TODO upsample array to make it compatible with size 14x14
                        pass
                #
                # if self.method == 'NetVLAD':
                #      pass
                # elif self.method == 'VGG16':
                stage1_activ_arr.append(stage1_activ)

                stage2_activ_arr.append(stage2_activ)

            if self.method1 == 'VGG16':
                stage1_descrip_arr, im_numbers = self.get_stage1_vgg16_descrip(dirb, stage1_activ_arr)
            elif self.method1 == 'NetVLAD':
                # image_batch, net_out, sess = self.prepare_NetVLAD()
                # db_array = self.add_baseline_netvlad(dirb, sess, net_out, image_batch)
                stage1_descrip_arr = np.squeeze(stage1_activ_arr, axis=1)
                im_numbers = im_numbers_netvlad
            elif self.method1 == 'ResNet':
                stage1_descrip_arr, im_numbers = self.get_stage1_resnet_descrip(dirb, stage1_activ_arr)
            elif self.method1 == 'GoogLeNet':
                stage1_descrip_arr, im_numbers = self.get_stage1_googlenet_descrip(dirb, stage1_activ_arr)

            stage1_descrip_arr = np.asarray(stage1_descrip_arr)

            # prepare spatial matching arrays
            stage2_activ_arr = np.asarray(stage2_activ_arr)
            hg, wg, depthg = stage2_activ_arr.shape[2], stage2_activ_arr.shape[3], stage2_activ_arr.shape[4]
            side = hg
            # side_eff = side // 2 - 1
            side_eff = side - 2 * self.sblk
            arr_size = side_eff ** 2

            self.channels_geom = np.arange(depthg)
            geom_array = np.zeros((len(dirb)*arr_size, 3 * 3 * depthg))

            cnt_geom_arr = 0
            im_numbers_local = []
            for idx, fname in enumerate(dirb):
                if idx % 1 == 0:
                    print(idx + b * self.batch_size, fname, "creating spatial matching features...")
                    self.textBrowser.append(str('{:<5}  {}  {}'.format(idx + b * self.batch_size, fname, "creating spatial matching features...")))
                    QApplication.processEvents()
                img_no = self.get_img_no(fname)
                stage2_activ = stage2_activ_arr[idx]

                # normalize along the direction of feature maps
                filter_sel_geom = pp.normalize(np.moveaxis(stage2_activ[0, :, :, self.channels_geom], 0, -1).
                                               reshape(side*side, depthg),  norm='l2', axis=1)
                filter_sel_geom = filter_sel_geom.reshape((side, side, depthg))

                # create  CNN cubes
                cnt = 0
                for cgii in range(self.sblk, hg - self.sblk, 1):
                    for cgjj in range(self.sblk, wg - self.sblk, 1):
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
            if self.method1 == 'NetVLAD':  # if NetVLAD, do not perform PCA
                stage1_projection = stage1_descrip_arr
            else:
                stage1_projection = pca.transform(stage1_descrip_arr)

            stage2_projection = pca_geom.transform(geom_array)

            # store batches
            stage1_projection_acc.append(stage1_projection)
            im_numbers_acc.append(im_numbers)
            stage2_projection_acc.append(stage2_projection)
            im_numbers_local_acc.append(im_numbers_local)

        # save databases to disk
        np.save('db/' + self.dataset_name + '_stage1_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1, np.vstack(stage1_projection_acc).astype('float32'))
        np.save('db/' + self.dataset_name + '_stage1_imgnum_'  + self.imageWidthLineEdit_s1.text() + '_' + self.method1, np.hstack(im_numbers_acc))
        np.save('db/' + self.dataset_name + '_stage2_' + self.imageWidthLineEdit_s2.text() + '_' + self.method2, np.vstack(stage2_projection_acc).astype('float32'))
        np.save('db/' + self.dataset_name + '_stage2_imgnum_' + self.imageWidthLineEdit_s2.text() + '_' + self.method2, np.hstack(im_numbers_local_acc))
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

    def get_candidates_vgg16(self, stage1_activ, im_numbers, nbrs0):
        """
        It provides the list of candidates (and distances) from IFDB by comparing VGG descriptors of the current query

        Parameters
        ----------
        stage1_activ: Descriptor
        im_numbers  : Reference image indexes
        channels    : Number of feature maps
        nbrs0       : Nearest Neighbor model

        Returns
        -------
        candidates  : The list of best candidates from the reference database
        cand_dist   : The vector distances between candidates and query
        img_hist    : The histogram of reference images

        """

        """Stage I for the VGG16 implementation.
        It gets the list of candidates (and distances) from IFDB by comparing CNN cubes of the current query"""

        img_hist = np.zeros(self.no_places, float)  # initialise histogram of distances
        h, w, depth = stage1_activ.shape[1], stage1_activ.shape[2], stage1_activ.shape[3]
        self.channels = np.arange(depth)
        img_activ_arr_ = np.moveaxis(stage1_activ[0, :, :, self.channels], 0, -1)

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
        # cutmeup = as_strided(img_activ_arr_, shape=(h - 2*self.lblk, h - 2*self.lblk, 512, 2*self.lblk+1, 2*self.lblk+1, 512), strides=2 * img_activ_arr_.strides)[:, :, 0, :, :, :]
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
                block = img_activ_arr_[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                block_descrip.append(pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.channels)), norm='l2', axis=1).flatten())
                cnt2 += 1

        # PCA dimensionality reduction
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
                    # img_hist_rep[file] += 1  # accumulate repetitions
                    img_hist[file] += 1      # accumulate distances

        # real_ncand = len(img_hist[img_hist != 0])
        # if real_ncand < self.ncand:
        #     real_ncand = self.ncand
        real_ncand = self.ncand

        candidates = np.argsort(-img_hist, axis=0)[:real_ncand]  # best top self.ncand candidates
        cand_dist = -np.sort(-img_hist, axis=0)[:real_ncand]  # best top candidates distances

        return candidates, cand_dist, img_hist

    def get_candidates_resnet(self, stage1_activ, im_numbers, nbrs0):
        """
        It provides the list of candidates (and distances) from IFDB by comparing ResNet descriptors of the current query

        Parameters
        ----------
        stage1_activ: Descriptor
        im_numbers  : Reference image indexes
        channels    : Number of feature maps
        nbrs0       : Nearest Neighbor model

        Returns
        -------
        candidates  : The list of best candidates from the reference database
        cand_dist   : The vector distances between candidates and query
        img_hist    : The histogram of reference images

        """

        img_hist = np.zeros(self.no_places, float)  # initialise histogram of distances
        h, w, depth = stage1_activ.shape[1], stage1_activ.shape[2], stage1_activ.shape[3]
        self.channels = np.arange(depth)
        img_activ_arr_ = np.moveaxis(stage1_activ[0, :, :, self.channels], 0, -1)

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
        # cutmeup = as_strided(img_activ_arr_, shape=(h - 2*self.lblk, h - 2*self.lblk, 512, 2*self.lblk+1, 2*self.lblk+1, 512), strides=2 * img_activ_arr_.strides)[:, :, 0, :, :, :]
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
                block = img_activ_arr_[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                block_descrip.append(pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.channels)), norm='l2', axis=1).flatten())
                cnt2 += 1

        # PCA dimensionality reduction
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
                    # img_hist_rep[file] += 1  # accumulate repetitions
                    img_hist[file] += 1      # accumulate distances

        # real_ncand = len(img_hist[img_hist != 0])
        # if real_ncand < self.ncand:
        #     real_ncand = self.ncand
        real_ncand = self.ncand

        candidates = np.argsort(-img_hist, axis=0)[:real_ncand]  # best top self.ncand candidates
        cand_dist = -np.sort(-img_hist, axis=0)[:real_ncand]  # best top candidates distances

        return candidates, cand_dist, img_hist

    def get_candidates_googlenet(self, stage1_activ, im_numbers, nbrs0):
        """
        It provides the list of candidates (and distances) from IFDB by comparing GoogLeNet descriptors of the current query

        Parameters
        ----------
        stage1_activ: Descriptor
        im_numbers  : Reference image indexes
        channels    : Number of feature maps
        nbrs0       : Nearest Neighbor model

        Returns
        -------
        candidates  : The list of best candidates from the reference database
        cand_dist   : The vector distances between candidates and query
        img_hist    : The histogram of reference images

        """

        """Stage I for the VGG16 implementation.
        It gets the list of candidates (and distances) from IFDB by comparing CNN cubes of the current query"""

        img_hist = np.zeros(self.no_places, float)  # initialise histogram of distances
        h, w, depth = stage1_activ.shape[1], stage1_activ.shape[2], stage1_activ.shape[3]
        self.channels = np.arange(depth)
        img_activ_arr_ = np.moveaxis(stage1_activ[0, :, :, self.channels], 0, -1)

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
        # cutmeup = as_strided(img_activ_arr_, shape=(h - 2*self.lblk, h - 2*self.lblk, 512, 2*self.lblk+1, 2*self.lblk+1, 512), strides=2 * img_activ_arr_.strides)[:, :, 0, :, :, :]
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
                block = img_activ_arr_[center[0] - self.lblk: center[0] + self.lblk + 1, center[1] - self.lblk: center[1] + self.lblk + 1]
                block_descrip.append(pp.normalize(block.reshape((2 * self.lblk + 1) ** 2, len(self.channels)), norm='l2', axis=1).flatten())
                cnt2 += 1

        # PCA dimensionality reduction
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
                    # img_hist_rep[file] += 1  # accumulate repetitions
                    img_hist[file] += 1      # accumulate distances

        # real_ncand = len(img_hist[img_hist != 0])
        # if real_ncand < self.ncand:
        #     real_ncand = self.ncand
        real_ncand = self.ncand

        candidates = np.argsort(-img_hist, axis=0)[:real_ncand]  # best top self.ncand candidates
        cand_dist = -np.sort(-img_hist, axis=0)[:real_ncand]  # best top candidates distances

        return candidates, cand_dist, img_hist

    def get_candidates_netvlad(self, descriptor, im_numbers, nbrs0):
        """
        It provides the list of candidates (and distances) from IFDB by comparing NetVLAD descriptor of the current query

        Parameters
        ----------
        stage1_activ: Descriptor
        im_numbers  : Reference image indexes
        nbrs0       : Nearest Neighbor model

        Returns
        -------
        candidates  : The list of best candidates from the reference database
        cand_dist   : The vector distances between candidates and query
        img_hist    : The histogram of reference images

        """

        # # PCA dimensionality reduction
        # stage1_activ = np.asarray(self.pca.transform(stage1_activ))

        img_hist = np.zeros(self.no_places, float)
        img_hist_rep = np.zeros(self.no_places, int)
        distances, indices = nbrs0.kneighbors(descriptor)

        if len(distances[0]) < self.ncand:
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

    def get_score_patch(self, query_indices,  cand_patches, nlr):
        """
        Gets the spatial matching score when using a patch around anchor points
        Parameters
        ----------
        query_indices: Index array of the best matches when comparing query and current candidate
        cand_patches : Patches with indexes in ascending order and null in the center.
        nlr          : The number of activations per side of the patch

        Returns
        -------
        score        : The spatial matching score for current candidate
        """

        patch_size = nlr
        nlr2 = nlr // 2

        # compare patches (too much overhead using GPU, CPU version preferred)
        if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
            query_indices_pad = np.pad(query_indices, (nlr2), 'constant', constant_values=-1000)
            query_indices_flat = query_indices.flatten()
            query_patches = image.extract_patches_2d(query_indices_pad, (patch_size, patch_size))

            # modify candidate patches to make it relative to each query closest match, so they can be compared
            cand_patches = np.add(cand_patches, query_indices_flat.reshape(query_indices.shape[0] ** 2, 1, 1))
            query_patches = torch.from_numpy(query_patches).to("cuda")
            cand_patches = torch.from_numpy(cand_patches).to("cuda")
            score = (query_patches == cand_patches).sum().cpu().item()
        else:

            # pad query array to allow for full patches near edges
            query_indices_pad = np.pad(query_indices, (nlr2), 'constant', constant_values=-1000)

            # extract patches
            query_patches = image.extract_patches_2d(query_indices_pad, (patch_size, patch_size))

            # modify candidate patches to make it relative to each query closest match, so they can be compared
            query_indices_flat = query_indices.flatten()
            cand_patches = np.add(cand_patches, query_indices_flat.reshape(query_indices.shape[0]**2, 1, 1))
            score = np.count_nonzero(query_patches == cand_patches)

        return score

    def get_score_patch0(self, query_indices,  nlr):
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


    # def create_query_vectors(self, hg, wg, vectors_query, array_geom_query, arr_size):# loop version
    #     cnt = 0
    #     for cgii in range(self.sblk, hg - self.sblk, 2):  # increment of 2 is to reduce complexity by skipping every other location
    #         for cgjj in range(self.sblk, wg - self.sblk, 2):
    #             if cnt == arr_size:
    #                 break
    #             center = (cgii, cgjj)
    #             block_geom_query = vectors_query[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]  # [:, :, 1:]
    #             array_geom_query[cnt] = block_geom_query
    #             cnt += 1
    #     array_geom_query = self.pca_geom.transform(array_geom_query.reshape(arr_size, 4608))
    #     return array_geom_query

    def select_method_stage1(self):
        """Select the checked option from the available methods in stage I"""

        if self.vggRadioButton.isChecked():
            self.method1 = 'VGG16'
            self.imageWidthLineEdit_s1.setText('224')
            self.imageSizeGroupBox_s1.setEnabled(False)
        elif self.netvladRadioButton.isChecked():
            self.method1 = 'NetVLAD'
            self.imageSizeGroupBox_s1.setEnabled(True)
        elif self.resnetRadioButton.isChecked():
            self.method1 = 'ResNet'
            self.imageWidthLineEdit_s1.setText('224')
            self.imageSizeGroupBox_s1.setEnabled(False)
        elif self.googlenetRadioButton.isChecked():
            self.method1 = 'GoogLeNet'
            self.imageWidthLineEdit_s1.setText('224')
            self.imageSizeGroupBox_s1.setEnabled(False)

    def select_method_stage2(self):
        """Select the checked option from the available methods in stage II"""

        if self.vggRadioButton_s2.isChecked():
            self.method2 = 'VGG16'
        elif self.resnetRadioButton_s2.isChecked():
            self.method2 = 'ResNet'
        elif self.googlenetRadioButton_s2.isChecked():
            self.method2 = 'GoogLeNet'

    def retrieve_model(self, method):
        """Retrieves chosen model for stage I """

        if method == 'VGG16':
            import vgg16_model
            if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                model_vgg16 = vgg16_model.VGG16Model('./checkpoints/vgg16_places365.npy').to('cuda').eval()
            else:
                model_vgg16 = vgg16_model.VGG16Model('./checkpoints/vgg16_places365.npy').eval()
            return model_vgg16

        elif method == 'NetVLAD':
            # create netvlad model
            base_model, net_vlad = self.create_base_and_netvlad_models()
            model = torch.nn.Module()
            model.add_module('encoder', base_model)
            model.add_module('pool', net_vlad)
            checkpoint = torch.load('./checkpoints/netvlad_checkpoint.pth.tar',
                                    map_location=lambda storage, loc: storage)
            model.load_state_dict(checkpoint['state_dict'], strict=False)
            model_netvlad = netvlad_model.EmbedNet(model)
            if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                model_netvlad = model_netvlad.cuda()
            return model_netvlad

        elif method == 'ResNet':
            import resnet_model
            if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                model_resnet = resnet_model.ResNetModel('./checkpoints/resnet-152-torch-places365.npy').to('cuda').eval()
            else:
                model_resnet = resnet_model.ResNetModel('./checkpoints/resnet-152-torch-places365.npy').eval()
            return model_resnet

        elif method == 'GoogLeNet':
            import googlenet_model
            if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                model_googlenet = googlenet_model.GoogLeNetModel('./checkpoints/googlenet_places365.npy').to('cuda').eval()
            else:
                model_googlenet = googlenet_model.GoogLeNetModel('./checkpoints/googlenet_places365.npy').eval()
        return model_googlenet

    def create_database(self):
        """Takes the images in the selected reference directory and creates CNN features databases for stages I and II"""

        # load models
        self.model_stage1 = self.retrieve_model(self.method1)
        if self.method2 == self.method1:
            self.model_stage2 = self.model_stage1
        else:
            self.model_stage2 = self.retrieve_model(self.method2)

        # initialize variables
        self.ref_dir = self.reference_folder + '/'
        # self.image_size1 = (224, 224)
        # self.image_size2 = (448, 448)
        # self.num_dim1 = 125
        # self.num_dim2 = 100
        # self.ns1 = 2000  # number of samples to train pca for stage I
        # self.ns2 = 2000  # number of samples to train pca for stage II
        self.lblk = 4    # 9x9 (x 512) CNN cubes
        self.sblk = 1    # 3x3 (x 512) CNN cubes
        self.batch_size = 250  # set value according to RAM resources
        # self.channels = np.arange(512)
        # self.channels_geom = np.arange(512)
        self.max_ncubes = 36
        self.refresh_view()

        self.preprocess1 = T.Compose([T.Resize(self.image_size1), T.CenterCrop(self.image_size1), T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), ])
        self.preprocess2 = T.Compose([T.Resize(self.image_size2), T.CenterCrop(self.image_size2), T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), ])

        self.create_db()

    def warning_win(self, title, message1, message2):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message1)
        msg.setInformativeText(message2)
        msg.setWindowTitle(title)
        msg.exec_()

    def get_query_geom_descrip(self, arr_size, vectors_query, hg, wg):
        """
        Calculate spatially-aware descriptors for query image

        Parameters
        ----------
        arr_size        : Number of descriptors
        vectors_query   : Activation tensor
        hg              : Number of activations in the vertical direction
        wg              : Number of activations in the horizontal direction

        Returns
        -------
        array_geom_query: Array of descriptors
        """
        self.channels_geom = np.arange(vectors_query.shape[2])

        # start = time.time()

        array_geom_query = image.extract_patches_2d(vectors_query, (2*self.sblk+1, 2*self.sblk+1))
        array_geom_query = self.pca_geom.transform(array_geom_query.reshape(arr_size, 3 * 3 * len(self.channels_geom)))

        # end = time.time()
        # print(end - start)

        # cnt = 0
        # array_geom_query = np.zeros((arr_size, 3, 3, len(self.channels_geom)))
        # for cgii in range(self.sblk, hg - self.sblk, 1):
        #     for cgjj in range(self.sblk, wg - self.sblk, 1):
        #         if cnt == arr_size:
        #             break
        #         center = (cgii, cgjj)
        #         block_geom_query = vectors_query[center[0] - self.sblk: center[0] + self.sblk + 1, center[1] - self.sblk: center[1] + self.sblk + 1]  # [:, :, 1:]
        #         array_geom_query[cnt] = block_geom_query
        #         cnt += 1
        # array_geom_query = self.pca_geom.transform(array_geom_query.reshape(arr_size, 3 * 3 * len(self.channels_geom)))

        return array_geom_query

    def use_frame_corr(self, npf, pf_arr, cand, i):
        """
        Exploits frame time correlation to boost recognition precision

        Parameters
        ----------
        npf     : Number of previous recognition outputs that are being considered
        pf_arr  : Array stoing previous recognition resuls
        cand    : Current candidate index
        i       : Image sequence index

        Returns
        -------
        wcand   : Weight of current candidate after considering frame correlation
        """

        wcand = 1  # candidate initial weight
        if i >= npf and npf != 0:
            fmax = 15
            accfp = 0
            max_accfp = 0
            for kk in range(npf):  # loop over past recognised events
                if len(pf_arr[:, 1]) == 1 or np.max(pf_arr[:, 1]) == 0:
                    strength = 1
                else:
                    # contribution of each past event based on recognition score
                    strength = pf_arr[npf - kk - 1, 1] / np.max(pf_arr[:, 1])

                # consider only those candidates within +-fmax distance of the past recognition being considered
                if np.abs(cand - (pf_arr[npf - kk - 1, 0])) <= fmax:
                    contrib = strength * (self.cp / fmax * (fmax - np.abs(cand - (pf_arr[npf - kk - 1, 0]))))
                    accfp += contrib

                    # select the maximum contribution
                    if contrib > max_accfp:
                        max_accfp = contrib
            wcand = 1 + max_accfp

        return wcand

    # @time_decorator
    def compute_neighbors(self, candidates, array_geom_query):
        """
        Calculates the index of the best match in the candidate for each feature in the query
        and for all candidates.
        Parameters
        ----------
        candidates      : Array containing the index of candidates in the spatial matching database (SMDB)
        array_geom_query: Query image descriptors

        Returns
        -------
        indices_arr_list: A list of arrays containing best matches between query and candidates' features
        """

        indices_arr_list = []
        # if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():  # loop version
        #     array_geom_query = torch.from_numpy(array_geom_query)
        #     array_geom_query = array_geom_query.to('cuda')
        #     candidates = torch.from_numpy(np.asarray(candidates)).to('cuda')
        #
        #     for c in range(0, self.ncand, 1):
        #         cand = candidates[c]
        #         array_geom_db = self.vectors_local[torch.nonzero(self.image_numbers_local == cand)].squeeze(dim=1)
        #         indices = torch.matmul(array_geom_query, torch.transpose(array_geom_db, 0, 1).double())
        #         indices = torch.argmin(1 - indices, dim=0)
        #         indices = indices.cpu().numpy()
        #         # indices = np.argmin(1 - indices, axis=0)
        #         indices_resh = indices.reshape((self.blocks_per_side, self.blocks_per_side))
        #         indices_arr_list.append(indices_resh)
        if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
            with torch.no_grad():
                array_geom_query = torch.from_numpy(array_geom_query)
                array_geom_query = array_geom_query.to('cuda')
                array_geom_query = array_geom_query.unsqueeze(0).repeat(self.ncand, 1, 1)  # replicate query array

                # SMDB database loaded on GPU
                if self.loadDbOnGpuCheckBox.isChecked():
                    candidates = torch.from_numpy(np.asarray(candidates)).to('cuda')
                    candidates = candidates.repeat_interleave(array_geom_query.shape[1]) * array_geom_query.shape[1]  # adapt candidates for indexing
                    ord_arr = torch.from_numpy(np.arange(array_geom_query.shape[1])).to('cuda')  # array of ascending numbers
                    ord_arr = ord_arr.repeat(self.ncand)  # replicate so it can be ddded to candidates
                    candidates = candidates + ord_arr
                    array_geom_db = self.vectors_local[candidates]  # extract vectors for candidates
                    array_geom_db = array_geom_db.split(array_geom_query.shape[1], dim=0)  # separate for each candidate
                    array_geom_db = torch.stack(array_geom_db)  # convert to tensor (result of split is a tuple)
                else:
                    # SMDB database on disk
                    candidates = np.asarray(candidates)
                    candidates = np.repeat(candidates, array_geom_query.shape[1]) * array_geom_query.shape[1]
                    ord_arr = np.arange(array_geom_query.shape[1])  # array of ascending numbers
                    ord_arr = np.tile(ord_arr, self.ncand)  # replicate so it can be added to candidates
                    candidates = candidates + ord_arr
                    array_geom_db = self.vectors_local[candidates]  # extract vectors for candidates
                    array_geom_db = np.asarray(np.split(array_geom_db, array_geom_query.shape[1])).\
                        reshape((self.ncand, array_geom_query.shape[1], array_geom_query.shape[2]))  # convert to tensor (result of split is a tuple)
                    array_geom_db = torch.from_numpy(array_geom_db).to('cuda')

                # let's split the batch of candidates (matrix multiplication can easily overflow memory)
                if self.gpu_max_candidates < self.ncand:
                    flag = False
                    nsplits = self.ncand // self.gpu_max_candidates   # number of splits
                    nelem = self.ncand // nsplits  # number of candidates per split
                    if self.ncand % self.gpu_max_candidates != 0:  # if there is some candidates remaining
                        nsplits =  nsplits + 1  # extend by one the number of splits
                        flag = True

                    for i in range(nsplits):
                        if not (flag and i == nsplits - 1):  # candidates in full splits
                            array_geom_query_split = array_geom_query[i*nelem: (i+1)*nelem]
                            array_geom_db_split = array_geom_db[i*nelem: (i+1)*nelem]
                        else:       # remaining candidates in last split
                            array_geom_query_split = array_geom_query[i*nelem: self.ncand]
                            array_geom_db_split = array_geom_db[i*nelem: self.ncand]

                        # this is the actual spatial matching, using matrix multiplication and extracting the candidate indexes of
                        # the best matches in the query for each feature
                        indices_split = torch.argmin(1 - torch.matmul(array_geom_query_split.half(), torch.transpose(array_geom_db_split.half(), 1, 2)), dim=1)

                        if i == 0:
                           indices = indices_split
                        else:
                            indices = torch.cat((indices, indices_split), 0)  # join the splits
                        torch.cuda.empty_cache()
                    indices = indices.reshape(-1, self.blocks_per_side, self.blocks_per_side)
                    indices_arr_list = list(indices.cpu().numpy())
                else:
                    # without splitting
                    indices = torch.argmin(1 - torch.matmul(array_geom_query.half(), torch.transpose(array_geom_db.half(), 1, 2)), dim=1)
                    indices = indices.reshape(-1, self.blocks_per_side, self.blocks_per_side)
                    indices_arr_list = list(indices.cpu().numpy())
                del array_geom_db, array_geom_query, candidates, ord_arr, indices
                torch.cuda.empty_cache()
        else:
            for c in range(0, self.ncand, 1):
                cand = candidates[c]

                # retrieve spatially-aware vectors from spatial matching database
                array_geom_db = self.vectors_local[np.where(self.image_numbers_local == cand)]

                # for each vector in the query, find the distances and indices of the nearest vectors in the current candidate
                indices = np.argmin(1 - np.inner(array_geom_query, array_geom_db), axis=0)
                indices_resh = indices.reshape((self.blocks_per_side, self.blocks_per_side))
                indices_arr_list.append(indices_resh)

        return indices_arr_list

    def recognise_places(self):
        """
        Performs recognition (stage II) based on the candidates provided by stage I
        """
        from torchvision import transforms as T

        self.refresh_view()
        self.preprocess1 = T.Compose([T.Resize(self.image_size1), T.CenterCrop(self.image_size1),
                                      T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), ])
        self.preprocess2 = T.Compose([T.Resize(self.image_size2), T.CenterCrop(self.image_size2),
                                      T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), ])

        self.model_stage1 = self.retrieve_model(self.method1)
        self.model_stage2 = self.retrieve_model(self.method2)

        self.reset_controls()
        self.refresh_view()

        start0 = time.time()
        from joblib import dump, load

        # define the models for each stage
        dirname = self.test_folder + '/'

        self.ncand = int(self.candidatesLineEdit.text())
        self.lblk = 4
        self.sblk = 1
        self.dirname = dirname
        # self.image_size1 = (int(self.imageWidthLineEdit_s1.text()), int(self.imageHeightLineEdit_s1.text()))
        # self.image_size2 = (int(self.imageWidthLineEdit_s2.text()), int(self.imageHeightLineEdit_s2.text()))
        self.max_ncubes = 36        # number of CNN cubes used in stage I
        self.cp = 0.4               # experimental frame correlation factor
        self.spatch = 19            # number of activations per side of the patch in stage II
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
            vectors = np.load('db/' + self.dataset_name + '_stage1_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1 + '.npy')
            nbrs0 = NearestNeighbors(n_neighbors=self.ncand, algorithm='brute').fit(vectors)  # brute  ball_tree  kd_tree  auto
            im_numbers = np.load('db/' + self.dataset_name + '_stage1_imgnum_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1 + '.npy')
            self.no_places = int(np.max(im_numbers)) + 1
        except:
            self.warning_win('Warning', 'Database for current settings not found or corrupted', 'Please load reference dir and create db')
            return 0

        try:
            self.vectors_local = np.load('db/'  + self.dataset_name + '_stage2_' + self.imageWidthLineEdit_s2.text() + '_' + self.method2 + '.npy')
            self.image_numbers_local = np.load('db/' + self.dataset_name + '_stage2_imgnum_'  + self.imageWidthLineEdit_s2.text() + '_' + self.method2 + '.npy')

            # load SMDB on GPU
            if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                if self.loadDbOnGpuCheckBox.isChecked():
                    self.vectors_local = torch.from_numpy(self.vectors_local)
                    self.image_numbers_local = torch.from_numpy(self.image_numbers_local)
                    self.vectors_local = self.vectors_local.to('cuda')
                    self.image_numbers_local = self.image_numbers_local.to('cuda')
        except:
            self.warning_win('Warning', 'Database for current settings not found', 'Please load reference dir and create db')
            return 0

        if self.method1 == 'NetVLAD':
            pass
            # self.pca = load('pca/pca_stage1_' + self.imageWidthLineEdit_s1.text() + '_NetVLAD.joblib')
        else:
            self.pca = load('pca/pca_stage1_' + self.imageWidthLineEdit_s1.text() + '_' + self.method1 + '.joblib')

        self.pca_geom = load('pca/pca_stage2_' + self.imageWidthLineEdit_s2.text() + '_' + self.method2 + '.joblib')

        if len(glob.glob(self.dirname + '/*.jpg')) != 0:
            filenames = glob.glob(self.dirname + '/*.jpg')
        elif len(glob.glob(self.dirname + '/*.png')) != 0:
            filenames = glob.glob(self.dirname + '/*.png')

         # write results to output file
        output = open(self.dataset + "_output.txt", "w")

        tpcnt = 0  # true positive counter
        fncnt = 0  # false negative counter
        fpcnt = 0  # false positive counter
        filenames.sort()
        score_arr = []
        time_arr = []
        res = []

        npf = self.npf   # number of previous frames considered
        pf_arr = np.zeros((npf, 2))
        same_img_score = 1E6

        import torch.nn.functional as F

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

            # read  query frame
            im = cv2.imread(fpath)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

            # get query vectors for both stages
            stage1_activ, stage2_activ = self.get_pytorch_tensors(fpath)

            hg, wg, depthg = stage2_activ.shape[1], stage2_activ.shape[2], stage2_activ.shape[3]
            channels_geom = np.arange(depthg)

            # maxpool the layer to make it compatible with code
            if self.method1 != 'NetVLAD':
                if stage1_activ.shape[1] > 14:
                    red_factor = stage1_activ.shape[1] // 14
                    stage1_activ = skimage.measure.block_reduce(stage1_activ, (1, red_factor, red_factor, 1), np.max)
                elif stage1_activ.shape[1] < 14:
                    # TODO upsample array to make it compatible with size 14x14
                    pass

            # call method for image filtering (stage I)
            if self.method1 == 'VGG16':
                candidates, cand_dist, img_hist = self.get_candidates_vgg16(stage1_activ, im_numbers, nbrs0)
            elif self.method1 == 'NetVLAD':
                candidates, cand_dist, img_hist = self.get_candidates_netvlad(stage1_activ, im_numbers, nbrs0)
            if self.method1 == 'ResNet':
                candidates, cand_dist, img_hist = self.get_candidates_resnet(stage1_activ, im_numbers, nbrs0)
            if self.method1 == 'GoogLeNet':
                candidates, cand_dist, img_hist = self.get_candidates_googlenet(stage1_activ, im_numbers, nbrs0)

            # get the query image number from its filename
            self.img_no = self.get_img_no(os.path.splitext(os.path.basename(fpath))[0])

            # get spatial matching vectors for query image
            im = cv2.resize(im, self.image_size2, interpolation=cv2.INTER_CUBIC)
            rows, cols, _ = im.shape

            side = stage2_activ.shape[1]
#            side_eff = side // 2 - 1
            side_eff = side - 2*self.sblk
            arr_size = side_eff ** 2
            vectors_query = pp.normalize(np.moveaxis(stage2_activ[0, :, :, channels_geom], 0, -1).reshape(side * side, depthg), norm='l2', axis=1)
            vectors_query = vectors_query.reshape((side, side, depthg))
            hg, wg, depthg = stage2_activ.shape[1], stage2_activ.shape[2], stage2_activ.shape[3]

            # declare k-NN model
#            nbrs_inst = NearestNeighbors(n_neighbors=1, algorithm='brute',leaf_size=500, metric='cosine')

            scores_hist = np.zeros(self.no_places, float)
            min_dist = np.zeros(self.no_places, float)
            min_dist[min_dist == 0] = 1E6
            self.blocks_per_side = side_eff
            # nlr = self.spatch // 2
            nlr = int(side_eff * 0.75)  # make patch side 75 % of image width
            if nlr % 2 == 0:
                nlr = nlr - 1
            nlr2 = nlr // 2

            # create list of patches with indexes in ascending order and null in the center. These are used during
            # spatial matching as the reference expected output in the ideal case of to identical query and candidate images
            cand_indices = np.arange(self.blocks_per_side**2).reshape((self.blocks_per_side, self.blocks_per_side)) - self.blocks_per_side**2 // 2
            candc0 = int(cand_indices.shape[1] / 2)
            cand_patch = cand_indices[candc0 - nlr2: candc0 + nlr2 + 1, candc0 - nlr2: candc0 + nlr2 + 1]
            cand_patch = cand_patch - cand_patch[nlr2, nlr2]
            cand_patches = np.stack([cand_patch  for i in range(self.blocks_per_side ** 2)], axis=0)

            # get maximum recognition score (as for identical images), which is used to calculate score percentage
            if i == 0:
                indices0 = np.arange(arr_size).reshape((self.blocks_per_side, self.blocks_per_side))
                same_img_score = self.get_score_patch(indices0, cand_patches, nlr)

            # train nearest neighbor for current query
            # self.nbrs, array_geom_query = self.train_nearest_neighbor(arr_size, vectors_query, hg, wg, nbrs_inst)

            # compute descriptors for query image
            array_geom_query = self.get_query_geom_descrip(arr_size, vectors_query, hg, wg)

            # calculate list of arrays of indexes of the best matches in each and all candidates for features in the query
            indices_arr = self.compute_neighbors(candidates, array_geom_query)

            if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                with torch.no_grad():
                    indices_arr = torch.from_numpy(np.asarray(indices_arr).
                                 reshape(self.ncand, 1, np.asarray(indices_arr).shape[1], np.asarray(indices_arr).shape[2])).to('cuda')

                    kh, kw = nlr, nlr  # patch size
                    dh, dw = 1, 1  # strides
                    cand_patches = cand_patches.reshape((self.blocks_per_side, self.blocks_per_side, 1, kw, kh))
                    cand_patches = torch.from_numpy(cand_patches).to('cuda')

                    # let's split the batch of candidates (matrix mutiplication can easily overflow memory)
                    if self.gpu_max_candidates < self.ncand:
                        flag = False
                        nsplits = self.ncand // self.gpu_max_candidates  # number of splits
                        nelem = self.ncand // nsplits  # number of candidates per split
                        if self.ncand % self.gpu_max_candidates != 0:  # if there is some candidates remaining
                            nsplits = nsplits + 1  # extend by one the number of splits
                            flag = True
                        for ii in range(nsplits):
                            if not (flag and ii == nsplits - 1):
                                _indices_arr_split = indices_arr[ii*nelem: (ii+1)*nelem]
                                _query_indices_pad = F.pad(_indices_arr_split, (nlr2, nlr2, nlr2, nlr2))
                                _query_patches = _query_indices_pad.unfold(2, kh, dh).unfold(3, kw, dw)
                                _query_patches = _query_patches.permute(0, 2, 3, 1, 4, 5).contiguous()
                                _cand_patches_split = cand_patches.unsqueeze(0).repeat(nelem, 1, 1, 1, 1, 1)
                                _indices_arr_flat = _indices_arr_split.reshape(nelem, self.blocks_per_side ** 2, 1, 1, 1)
                                _cand_patches_flat = _cand_patches_split.reshape(nelem, self.blocks_per_side ** 2, 1, nlr, nlr)
                                _cand_patches_flat = torch.add(_indices_arr_flat, _cand_patches_flat)
                                _cand_patches = _cand_patches_flat.reshape((nelem, self.blocks_per_side, self.blocks_per_side, 1, nlr, nlr))

                                _score = (_query_patches == _cand_patches).view(nelem, -1).sum(1)
                                _score = _score.cpu().numpy()
                                del _query_patches, _indices_arr_split, _indices_arr_flat, _cand_patches_flat, _query_indices_pad

                            else:
                                rest_elem = indices_arr.shape[0] - ii * nelem
                                _indices_arr_split = indices_arr[ii*nelem: indices_arr.shape[0]]
                                _query_indices_pad = F.pad(_indices_arr_split, (nlr2, nlr2, nlr2, nlr2))
                                _query_patches = _query_indices_pad.unfold(2, kh, dh).unfold(3, kw, dw)
                                _query_patches = _query_patches.permute(0, 2, 3, 1, 4, 5).contiguous()
                                _cand_patches_split = cand_patches.unsqueeze(0).repeat(rest_elem, 1, 1, 1, 1, 1)
                                _indices_arr_flat = _indices_arr_split.reshape(rest_elem, self.blocks_per_side ** 2, 1, 1, 1)
                                _cand_patches_flat = _cand_patches_split.reshape(rest_elem, self.blocks_per_side ** 2, 1, nlr, nlr)
                                _cand_patches_flat = torch.add(_indices_arr_flat, _cand_patches_flat)
                                _cand_patches = _cand_patches_flat.reshape((rest_elem, self.blocks_per_side, self.blocks_per_side, 1, nlr, nlr))

                                _score = (_query_patches == _cand_patches).view(rest_elem, -1).sum(1)
                                _score = _score.cpu().numpy()
                                del _query_patches, _indices_arr_split, _indices_arr_flat, _cand_patches_flat, _query_indices_pad

                            if ii == 0:
                                scores = _score
                            else:
                                scores = np.concatenate((scores, _score), 0)
                            torch.cuda.empty_cache()
                    else:
                        # indices_arr = torch.from_numpy(np.asarray(indices_arr).
                        #             reshape(self.ncand, 1, np.asarray(indices_arr).shape[1], np.asarray(indices_arr).shape[2])).to('cuda')
                        kh, kw = nlr, nlr   # patch size
                        dh, dw = 1, 1       # strides
                        query_indices_pad = F.pad(indices_arr, (nlr2, nlr2, nlr2, nlr2))
                        query_patches = query_indices_pad.unfold(2, kh, dh).unfold(3, kw, dw)
                        query_patches = query_patches.permute(0, 2, 3, 1, 4, 5).contiguous()

                        cand_patches = cand_patches.reshape((self.blocks_per_side, self.blocks_per_side, 1, kw, kh))
                        cand_patches = cand_patches.unsqueeze(0).repeat(self.ncand, 1, 1, 1, 1, 1)

                        indices_arr_flat = indices_arr.reshape(self.ncand, self.blocks_per_side**2, 1, 1, 1)
                        cand_patches_flat = cand_patches.reshape(self.ncand, self.blocks_per_side**2, 1, nlr, nlr)
                        cand_patches_flat = torch.add(indices_arr_flat, cand_patches_flat)
                        cand_patches = cand_patches_flat.reshape((self.ncand, self.blocks_per_side, self.blocks_per_side, 1, nlr, nlr))

                        query_patches = query_patches.to('cuda')
                        cand_patches = cand_patches.to('cuda')
                        scores = (query_patches == cand_patches).view(self.ncand, -1).sum(1)
                        del cand_patch, query_patches, indices_arr, indices_arr_flat, cand_patches_flat, query_indices_pad
                        torch.cuda.empty_cache()
                        scores = scores.cpu().numpy()

            # loop over candidates for stage I
            for c in range(0, self.ncand, 1):
                cand = candidates[c]

                if torch.cuda.is_available() and self.useGpuCheckBox.isChecked():
                   score = scores[c]
                else:
                    query_indices = indices_arr[c]

                    # get score for current candidate
                    score = self.get_score_patch(query_indices, cand_patches, nlr)

                # exploit frame correlation
                wcand = self.use_frame_corr(npf, pf_arr, cand, i)

                # weight histogram bin taking past recognitions into account
                scores_hist[cand] = score * wcand

                # if i > 10 and i % 10 != 0 and score * wcand * 100 / float(same_img_score) > mean_score + self.ecut * std_score:
                #     print(mean_score, c)
                #     break

            # select highest bin in  histogram as recognised place
            hit = np.argmax(scores_hist)
            score = np.max(scores_hist)

            # uncomment this to calculate steering (used for teach&play navigation based on VPR)
            # steer = self.get_hor_offset_patch(nbrs_inst, array_geom_query, array_geom_db, nlr)
#            print(np.round(steer*100, 2), '''%''')

            # keep track of previously recognised events
            if npf != 0:
                for pfcnt in np.arange(npf-1):
                    pf_arr[pfcnt, 0] = pf_arr[pfcnt + 1, 0]  # store recognition frame
                    pf_arr[pfcnt, 1] = pf_arr[pfcnt + 1, 1]  # store recognition score
                pf_arr[npf-1, 0] = int(hit)
                pf_arr[npf-1, 1] = np.round(score, 2)

            score = score * 100. / same_img_score #  referred to the score of identical images being compared
            if i % 10 == 0:
                score_arr.append(score)
                mean_score = np.mean(np.asarray(score_arr))
                std_score = np.std(np.asarray(score_arr))
            end_imgt = time.time()
            time_arr.append(end_imgt - start_imgt)

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

            res.append((str(i), hit))
        output.close()

        end0 = time.time()

        color = QtGui.QColor(0,0,0)  # black
        self.textBrowser.setTextColor(color)
        self.textBrowser.append("Recognition finished")
        return accuracy, precision, recall, end0 - start0, np.round(np.mean(np.asarray(time_arr)), 2)


class Plot_PR_curves(QRunnable):

    def __init__(self, frameTolLineEdit, pr_file):
        super(Plot_PR_curves, self).__init__()
        self.frameTolLineEdit = frameTolLineEdit
        self.pr_file = pr_file

    # plot_PR_curves
    def run(self):

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
        plt.pause(0.1)

    def create_PR_data(self):
        import csv
        import numpy as np

        img_sep = int(self.frameTolLineEdit)
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



