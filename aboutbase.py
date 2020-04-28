# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutbox.ui'
#
# Created: Sun Jan 21 15:13:58 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

# from PySide2 import QtCore, QtGui
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QIcon, QPixmap, QFont

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(832, 364)
        self.gridLayout = qtw.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = qtw.QLabel(Dialog)
        self.label.setMaximumSize(QtCore.QSize(500, 300))
        self.label.setText("")
        self.label.setPixmap(QPixmap("init.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = qtw.QLabel(Dialog)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 320))
        font = QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.buttonBox = qtw.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(qtw.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(Dialog)
        # QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        self.buttonBox.accepted.connect(Dialog.accept)
        # QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        self.buttonBox.rejected.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(qtw.QApplication.translate("Dialog", "MESG - About", None))
        self.label_2.setText(qtw.QApplication.translate("Dialog", "SSM-VPR Version 1.0.0\n"
                                                                    "\n"
                                                                    "SSM-VPR is an interface for testing datasets on the task \n"
                                                                    "of visual place recognition.\n"
                                                                    "\n"
                                                                    "Created by Luis G. Camara", None))

