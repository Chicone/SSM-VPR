import cv2
import numpy as np
import tensorflow as tf
import os
import sys

import netvlad_tf.net_from_mat as nfm
import netvlad_tf.nets as nets

def progressBar(value, endvalue, bar_length=20):

        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
        sys.stdout.flush()
        
def PredictNetVlad(ref_dir):
        results = []
        imageNo = []
        fnames = []
        #prepare netvlad model
        tf.reset_default_graph()
        image_batch = tf.placeholder(
                dtype=tf.float32, shape=[None, None, None, 3])
        net_out = nets.vgg16NetvladPca(image_batch)
        saver = tf.train.Saver()
        sess = tf.Session()
        saver.restore(sess, nets.defaultCheckpoint())

        #get name of dataset
        dataset = os.path.split(os.path.split(ref_dir[:-1])[0])[1]
        dir = [d for d in os.listdir(ref_dir)]

        for idx, fname in enumerate(dir):
                fnames.append(fname)
                progressBar(idx, len(dir))

                if dataset == 'Nordland_synthesized':
                        img_no = int(os.path.splitext(os.path.basename(fname))[0])
                else:
                        img_no = int(os.path.basename(fname)[5:9])

                imageNo.append(img_no)
                fpath = ref_dir + '/' + fname
                im = cv2.imread(fpath)
                # im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                batch = np.expand_dims(im, axis=0)

                descriptor = sess.run(net_out, feed_dict={image_batch: batch})
                results.append(descriptor[0])
        return results, imageNo, fnames