# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ssm.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1262, 783)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(1200, 730))
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox_7 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_7.setGeometry(QtCore.QRect(590, 299, 671, 411))
        self.groupBox_7.setObjectName("groupBox_7")
        self.queryGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.queryGroupBox.setGeometry(QtCore.QRect(590, 30, 224, 231))
        self.queryGroupBox.setStyleSheet("")
        self.queryGroupBox.setObjectName("queryGroupBox")
        self.scrollArea = QtWidgets.QScrollArea(self.queryGroupBox)
        self.scrollArea.setGeometry(QtCore.QRect(0, 20, 221, 211))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 219, 209))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.queryImageLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.queryImageLabel.setGeometry(QtCore.QRect(0, 0, 224, 224))
        self.queryImageLabel.setText("")
        self.queryImageLabel.setObjectName("queryImageLabel")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.stage1_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.stage1_groupBox.setEnabled(True)
        self.stage1_groupBox.setGeometry(QtCore.QRect(30, 30, 161, 411))
        self.stage1_groupBox.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.stage1_groupBox.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.stage1_groupBox.setObjectName("stage1_groupBox")
        self.imageSizeGroupBox_s1 = QtWidgets.QGroupBox(self.stage1_groupBox)
        self.imageSizeGroupBox_s1.setGeometry(QtCore.QRect(10, 30, 141, 101))
        self.imageSizeGroupBox_s1.setMaximumSize(QtCore.QSize(160, 16777215))
        self.imageSizeGroupBox_s1.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.imageSizeGroupBox_s1.setObjectName("imageSizeGroupBox_s1")
        self.imageWidthLineEdit_s1 = QtWidgets.QLineEdit(self.imageSizeGroupBox_s1)
        self.imageWidthLineEdit_s1.setGeometry(QtCore.QRect(60, 30, 41, 27))
        self.imageWidthLineEdit_s1.setAutoFillBackground(False)
        self.imageWidthLineEdit_s1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.imageWidthLineEdit_s1.setReadOnly(False)
        self.imageWidthLineEdit_s1.setPlaceholderText("")
        self.imageWidthLineEdit_s1.setObjectName("imageWidthLineEdit_s1")
        self.imageHeightLineEdit_s1 = QtWidgets.QLineEdit(self.imageSizeGroupBox_s1)
        self.imageHeightLineEdit_s1.setGeometry(QtCore.QRect(60, 65, 41, 27))
        self.imageHeightLineEdit_s1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.imageHeightLineEdit_s1.setReadOnly(False)
        self.imageHeightLineEdit_s1.setObjectName("imageHeightLineEdit_s1")
        self.label = QtWidgets.QLabel(self.imageSizeGroupBox_s1)
        self.label.setGeometry(QtCore.QRect(10, 30, 80, 30))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.imageSizeGroupBox_s1)
        self.label_2.setGeometry(QtCore.QRect(7, 70, 66, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.imageSizeGroupBox_s1)
        self.label_3.setGeometry(QtCore.QRect(110, 30, 21, 30))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.imageSizeGroupBox_s1)
        self.label_4.setGeometry(QtCore.QRect(110, 70, 30, 20))
        self.label_4.setObjectName("label_4")
        self.groupBox_2 = QtWidgets.QGroupBox(self.stage1_groupBox)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 140, 141, 151))
        self.groupBox_2.setMaximumSize(QtCore.QSize(160, 16777215))
        self.groupBox_2.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.groupBox_2.setObjectName("groupBox_2")
        self.vggRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.vggRadioButton.setGeometry(QtCore.QRect(20, 30, 115, 22))
        self.vggRadioButton.setObjectName("vggRadioButton")
        self.netvladRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.netvladRadioButton.setGeometry(QtCore.QRect(20, 122, 115, 20))
        self.netvladRadioButton.setObjectName("netvladRadioButton")
        self.resnetRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.resnetRadioButton.setGeometry(QtCore.QRect(20, 60, 115, 22))
        self.resnetRadioButton.setObjectName("resnetRadioButton")
        self.googlenetRadioButton = QtWidgets.QRadioButton(self.groupBox_2)
        self.googlenetRadioButton.setGeometry(QtCore.QRect(20, 90, 115, 22))
        self.googlenetRadioButton.setObjectName("googlenetRadioButton")
        self.groupBox_8 = QtWidgets.QGroupBox(self.stage1_groupBox)
        self.groupBox_8.setGeometry(QtCore.QRect(10, 300, 141, 100))
        self.groupBox_8.setMaximumSize(QtCore.QSize(160, 16777215))
        self.groupBox_8.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.groupBox_8.setObjectName("groupBox_8")
        self.pcaDimLineEdit_s1 = QtWidgets.QLineEdit(self.groupBox_8)
        self.pcaDimLineEdit_s1.setGeometry(QtCore.QRect(80, 20, 51, 27))
        self.pcaDimLineEdit_s1.setAutoFillBackground(False)
        self.pcaDimLineEdit_s1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pcaDimLineEdit_s1.setReadOnly(False)
        self.pcaDimLineEdit_s1.setPlaceholderText("")
        self.pcaDimLineEdit_s1.setObjectName("pcaDimLineEdit_s1")
        self.label_21 = QtWidgets.QLabel(self.groupBox_8)
        self.label_21.setGeometry(QtCore.QRect(10, 20, 80, 30))
        self.label_21.setObjectName("label_21")
        self.label_22 = QtWidgets.QLabel(self.groupBox_8)
        self.label_22.setGeometry(QtCore.QRect(10, 50, 80, 30))
        self.label_22.setObjectName("label_22")
        self.pcaSamplesLineEdit_s1 = QtWidgets.QLineEdit(self.groupBox_8)
        self.pcaSamplesLineEdit_s1.setGeometry(QtCore.QRect(80, 50, 51, 27))
        self.pcaSamplesLineEdit_s1.setAutoFillBackground(False)
        self.pcaSamplesLineEdit_s1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pcaSamplesLineEdit_s1.setReadOnly(False)
        self.pcaSamplesLineEdit_s1.setPlaceholderText("")
        self.pcaSamplesLineEdit_s1.setObjectName("pcaSamplesLineEdit_s1")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(30, 460, 531, 131))
        self.groupBox_3.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.groupBox_3.setObjectName("groupBox_3")
        self.btnLoadReference = QtWidgets.QPushButton(self.groupBox_3)
        self.btnLoadReference.setGeometry(QtCore.QRect(20, 24, 101, 27))
        self.btnLoadReference.setObjectName("btnLoadReference")
        self.btnLoadTest = QtWidgets.QPushButton(self.groupBox_3)
        self.btnLoadTest.setGeometry(QtCore.QRect(20, 60, 101, 27))
        self.btnLoadTest.setObjectName("btnLoadTest")
        self.btnLoadGroungTruth = QtWidgets.QPushButton(self.groupBox_3)
        self.btnLoadGroungTruth.setGeometry(QtCore.QRect(20, 96, 101, 27))
        self.btnLoadGroungTruth.setObjectName("btnLoadGroungTruth")
        self.refOkLabel = QtWidgets.QLabel(self.groupBox_3)
        self.refOkLabel.setGeometry(QtCore.QRect(130, 30, 391, 17))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.refOkLabel.setFont(font)
        self.refOkLabel.setText("")
        self.refOkLabel.setObjectName("refOkLabel")
        self.testOkLabel = QtWidgets.QLabel(self.groupBox_3)
        self.testOkLabel.setGeometry(QtCore.QRect(130, 66, 391, 17))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.testOkLabel.setFont(font)
        self.testOkLabel.setText("")
        self.testOkLabel.setObjectName("testOkLabel")
        self.groundTruthOkLabel = QtWidgets.QLabel(self.groupBox_3)
        self.groundTruthOkLabel.setGeometry(QtCore.QRect(130, 103, 391, 17))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.groundTruthOkLabel.setFont(font)
        self.groundTruthOkLabel.setText("")
        self.groundTruthOkLabel.setObjectName("groundTruthOkLabel")
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(30, 610, 161, 111))
        self.groupBox_4.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.groupBox_4.setObjectName("groupBox_4")
        self.btnCreateDB = QtWidgets.QPushButton(self.groupBox_4)
        self.btnCreateDB.setGeometry(QtCore.QRect(30, 30, 91, 27))
        self.btnCreateDB.setObjectName("btnCreateDB")
        self.btnRecognition = QtWidgets.QPushButton(self.groupBox_4)
        self.btnRecognition.setGeometry(QtCore.QRect(30, 70, 91, 27))
        self.btnRecognition.setObjectName("btnRecognition")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(590, 320, 671, 401))
        font = QtGui.QFont()
        font.setFamily("Monospace")
        font.setPointSize(8)
        self.textBrowser.setFont(font)
        self.textBrowser.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.textBrowser.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.textBrowser.setObjectName("textBrowser")
        self.outputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputGroupBox.setGeometry(QtCore.QRect(810, 30, 224, 231))
        self.outputGroupBox.setStyleSheet("")
        self.outputGroupBox.setObjectName("outputGroupBox")
        self.scrollArea_4 = QtWidgets.QScrollArea(self.outputGroupBox)
        self.scrollArea_4.setGeometry(QtCore.QRect(0, 20, 221, 211))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea_4.sizePolicy().hasHeightForWidth())
        self.scrollArea_4.setSizePolicy(sizePolicy)
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollArea_4.setObjectName("scrollArea_4")
        self.scrollAreaWidgetContents_4 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_4.setGeometry(QtCore.QRect(0, 0, 219, 209))
        self.scrollAreaWidgetContents_4.setObjectName("scrollAreaWidgetContents_4")
        self.outputImageLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents_4)
        self.outputImageLabel.setGeometry(QtCore.QRect(0, 0, 224, 224))
        self.outputImageLabel.setText("")
        self.outputImageLabel.setObjectName("outputImageLabel")
        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_4)
        self.referenceGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.referenceGroupBox.setGeometry(QtCore.QRect(1030, 30, 224, 231))
        self.referenceGroupBox.setStyleSheet("")
        self.referenceGroupBox.setObjectName("referenceGroupBox")
        self.scrollArea_6 = QtWidgets.QScrollArea(self.referenceGroupBox)
        self.scrollArea_6.setGeometry(QtCore.QRect(0, 20, 221, 211))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea_6.sizePolicy().hasHeightForWidth())
        self.scrollArea_6.setSizePolicy(sizePolicy)
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollArea_6.setObjectName("scrollArea_6")
        self.scrollAreaWidgetContents_6 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_6.setGeometry(QtCore.QRect(0, 0, 219, 209))
        self.scrollAreaWidgetContents_6.setObjectName("scrollAreaWidgetContents_6")
        self.referenceImageLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents_6)
        self.referenceImageLabel.setGeometry(QtCore.QRect(1, 0, 224, 224))
        self.referenceImageLabel.setText("")
        self.referenceImageLabel.setObjectName("referenceImageLabel")
        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_6)
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setGeometry(QtCore.QRect(400, 610, 161, 111))
        self.groupBox_5.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.groupBox_5.setObjectName("groupBox_5")
        self.btnPause = QtWidgets.QPushButton(self.groupBox_5)
        self.btnPause.setGeometry(QtCore.QRect(30, 30, 91, 27))
        self.btnPause.setObjectName("btnPause")
        self.btnStop = QtWidgets.QPushButton(self.groupBox_5)
        self.btnStop.setGeometry(QtCore.QRect(30, 70, 91, 27))
        self.btnStop.setObjectName("btnStop")
        self.stage2_groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.stage2_groupBox.setGeometry(QtCore.QRect(210, 30, 161, 411))
        self.stage2_groupBox.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.stage2_groupBox.setObjectName("stage2_groupBox")
        self.groupBox_10 = QtWidgets.QGroupBox(self.stage2_groupBox)
        self.groupBox_10.setGeometry(QtCore.QRect(10, 30, 141, 101))
        self.groupBox_10.setMaximumSize(QtCore.QSize(160, 16777215))
        self.groupBox_10.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.groupBox_10.setObjectName("groupBox_10")
        self.imageWidthLineEdit_s2 = QtWidgets.QLineEdit(self.groupBox_10)
        self.imageWidthLineEdit_s2.setGeometry(QtCore.QRect(60, 29, 41, 27))
        self.imageWidthLineEdit_s2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.imageWidthLineEdit_s2.setReadOnly(False)
        self.imageWidthLineEdit_s2.setPlaceholderText("")
        self.imageWidthLineEdit_s2.setObjectName("imageWidthLineEdit_s2")
        self.imageHeightLineEdit_s2 = QtWidgets.QLineEdit(self.groupBox_10)
        self.imageHeightLineEdit_s2.setGeometry(QtCore.QRect(60, 63, 41, 30))
        self.imageHeightLineEdit_s2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.imageHeightLineEdit_s2.setReadOnly(False)
        self.imageHeightLineEdit_s2.setObjectName("imageHeightLineEdit_s2")
        self.label_8 = QtWidgets.QLabel(self.groupBox_10)
        self.label_8.setGeometry(QtCore.QRect(10, 30, 80, 30))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.groupBox_10)
        self.label_9.setGeometry(QtCore.QRect(7, 70, 66, 16))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.groupBox_10)
        self.label_10.setGeometry(QtCore.QRect(110, 30, 21, 30))
        self.label_10.setObjectName("label_10")
        self.label_13 = QtWidgets.QLabel(self.groupBox_10)
        self.label_13.setGeometry(QtCore.QRect(110, 66, 30, 31))
        self.label_13.setObjectName("label_13")
        self.groupBox_9 = QtWidgets.QGroupBox(self.stage2_groupBox)
        self.groupBox_9.setGeometry(QtCore.QRect(10, 140, 141, 151))
        self.groupBox_9.setMaximumSize(QtCore.QSize(160, 16777215))
        self.groupBox_9.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.groupBox_9.setObjectName("groupBox_9")
        self.vggRadioButton_s2 = QtWidgets.QRadioButton(self.groupBox_9)
        self.vggRadioButton_s2.setGeometry(QtCore.QRect(20, 30, 115, 22))
        self.vggRadioButton_s2.setObjectName("vggRadioButton_s2")
        self.resnetRadioButton_s2 = QtWidgets.QRadioButton(self.groupBox_9)
        self.resnetRadioButton_s2.setGeometry(QtCore.QRect(20, 60, 115, 22))
        self.resnetRadioButton_s2.setObjectName("resnetRadioButton_s2")
        self.googlenetRadioButton_s2 = QtWidgets.QRadioButton(self.groupBox_9)
        self.googlenetRadioButton_s2.setGeometry(QtCore.QRect(20, 90, 115, 22))
        self.googlenetRadioButton_s2.setObjectName("googlenetRadioButton_s2")
        self.groupBox_11 = QtWidgets.QGroupBox(self.stage2_groupBox)
        self.groupBox_11.setGeometry(QtCore.QRect(10, 300, 141, 100))
        self.groupBox_11.setMaximumSize(QtCore.QSize(160, 16777215))
        self.groupBox_11.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.groupBox_11.setObjectName("groupBox_11")
        self.pcaDimLineEdit_s2 = QtWidgets.QLineEdit(self.groupBox_11)
        self.pcaDimLineEdit_s2.setGeometry(QtCore.QRect(80, 20, 51, 27))
        self.pcaDimLineEdit_s2.setAutoFillBackground(False)
        self.pcaDimLineEdit_s2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pcaDimLineEdit_s2.setReadOnly(False)
        self.pcaDimLineEdit_s2.setPlaceholderText("")
        self.pcaDimLineEdit_s2.setObjectName("pcaDimLineEdit_s2")
        self.label_23 = QtWidgets.QLabel(self.groupBox_11)
        self.label_23.setGeometry(QtCore.QRect(10, 20, 80, 30))
        self.label_23.setObjectName("label_23")
        self.label_24 = QtWidgets.QLabel(self.groupBox_11)
        self.label_24.setGeometry(QtCore.QRect(10, 50, 80, 30))
        self.label_24.setObjectName("label_24")
        self.pcaSamplesLineEdit_s2 = QtWidgets.QLineEdit(self.groupBox_11)
        self.pcaSamplesLineEdit_s2.setGeometry(QtCore.QRect(80, 50, 51, 27))
        self.pcaSamplesLineEdit_s2.setAutoFillBackground(False)
        self.pcaSamplesLineEdit_s2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pcaSamplesLineEdit_s2.setReadOnly(False)
        self.pcaSamplesLineEdit_s2.setPlaceholderText("")
        self.pcaSamplesLineEdit_s2.setObjectName("pcaSamplesLineEdit_s2")
        self.groupBox_6 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_6.setGeometry(QtCore.QRect(220, 610, 161, 111))
        self.groupBox_6.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"\n"
"")
        self.groupBox_6.setObjectName("groupBox_6")
        self.btnSaveOutput = QtWidgets.QPushButton(self.groupBox_6)
        self.btnSaveOutput.setGeometry(QtCore.QRect(30, 30, 91, 27))
        self.btnSaveOutput.setObjectName("btnSaveOutput")
        self.btnPRcurves = QtWidgets.QPushButton(self.groupBox_6)
        self.btnPRcurves.setGeometry(QtCore.QRect(30, 70, 91, 27))
        self.btnPRcurves.setObjectName("btnPRcurves")
        self.groupBox_12 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_12.setGeometry(QtCore.QRect(390, 30, 171, 151))
        self.groupBox_12.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.groupBox_12.setObjectName("groupBox_12")
        self.label_17 = QtWidgets.QLabel(self.groupBox_12)
        self.label_17.setGeometry(QtCore.QRect(10, 65, 111, 30))
        self.label_17.setObjectName("label_17")
        self.frameTolLineEdit = QtWidgets.QLineEdit(self.groupBox_12)
        self.frameTolLineEdit.setGeometry(QtCore.QRect(125, 65, 38, 27))
        self.frameTolLineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.frameTolLineEdit.setObjectName("frameTolLineEdit")
        self.candidatesLineEdit = QtWidgets.QLineEdit(self.groupBox_12)
        self.candidatesLineEdit.setGeometry(QtCore.QRect(125, 31, 38, 27))
        self.candidatesLineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.candidatesLineEdit.setObjectName("candidatesLineEdit")
        self.label_18 = QtWidgets.QLabel(self.groupBox_12)
        self.label_18.setGeometry(QtCore.QRect(10, 32, 81, 30))
        self.label_18.setObjectName("label_18")
        self.prevFramesLineEdit = QtWidgets.QLineEdit(self.groupBox_12)
        self.prevFramesLineEdit.setGeometry(QtCore.QRect(125, 100, 38, 27))
        self.prevFramesLineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.prevFramesLineEdit.setObjectName("prevFramesLineEdit")
        self.label_5 = QtWidgets.QLabel(self.groupBox_12)
        self.label_5.setGeometry(QtCore.QRect(10, 100, 111, 31))
        self.label_5.setText("Frame corr. (FC)")
        self.label_5.setObjectName("label_5")
        self.gpuGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.gpuGroupBox.setGeometry(QtCore.QRect(390, 280, 171, 161))
        self.gpuGroupBox.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 3px;\n"
"    padding: 3 0 3 0;\n"
"}\n"
"")
        self.gpuGroupBox.setObjectName("gpuGroupBox")
        self.label_12 = QtWidgets.QLabel(self.gpuGroupBox)
        self.label_12.setGeometry(QtCore.QRect(10, 80, 111, 31))
        self.label_12.setText("Max. candidates ")
        self.label_12.setObjectName("label_12")
        self.gpuCandLineEdit = QtWidgets.QLineEdit(self.gpuGroupBox)
        self.gpuCandLineEdit.setGeometry(QtCore.QRect(125, 80, 38, 27))
        self.gpuCandLineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.gpuCandLineEdit.setObjectName("gpuCandLineEdit")
        self.loadDbOnGpuCheckBox = QtWidgets.QCheckBox(self.gpuGroupBox)
        self.loadDbOnGpuCheckBox.setGeometry(QtCore.QRect(10, 40, 141, 22))
        self.loadDbOnGpuCheckBox.setObjectName("loadDbOnGpuCheckBox")
        self.useGpuCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.useGpuCheckBox.setGeometry(QtCore.QRect(390, 250, 96, 22))
        self.useGpuCheckBox.setObjectName("useGpuCheckBox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1262, 25))
        self.menuBar.setObjectName("menuBar")
        self.menuAbout = QtWidgets.QMenu(self.menuBar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menuBar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSpectrogram = QtWidgets.QAction(MainWindow)
        self.actionSpectrogram.setObjectName("actionSpectrogram")
        self.actionFrequency_Map = QtWidgets.QAction(MainWindow)
        self.actionFrequency_Map.setObjectName("actionFrequency_Map")
        self.actionSave_path = QtWidgets.QAction(MainWindow)
        self.actionSave_path.setObjectName("actionSave_path")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuAbout.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Visual Place Recognition  interface"))
        self.groupBox_7.setTitle(_translate("MainWindow", "Console"))
        self.queryGroupBox.setTitle(_translate("MainWindow", "Query"))
        self.stage1_groupBox.setTitle(_translate("MainWindow", "STAGE I "))
        self.imageSizeGroupBox_s1.setTitle(_translate("MainWindow", "Image size"))
        self.imageWidthLineEdit_s1.setText(_translate("MainWindow", "224"))
        self.imageHeightLineEdit_s1.setText(_translate("MainWindow", "224"))
        self.label.setText(_translate("MainWindow", "Width"))
        self.label_2.setText(_translate("MainWindow", "Height"))
        self.label_3.setText(_translate("MainWindow", "px"))
        self.label_4.setText(_translate("MainWindow", "px"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Method"))
        self.vggRadioButton.setText(_translate("MainWindow", "VGG16"))
        self.netvladRadioButton.setText(_translate("MainWindow", "NetVLAD"))
        self.resnetRadioButton.setText(_translate("MainWindow", "ResNet"))
        self.googlenetRadioButton.setText(_translate("MainWindow", "GoogLeNet"))
        self.groupBox_8.setTitle(_translate("MainWindow", "PCA"))
        self.pcaDimLineEdit_s1.setText(_translate("MainWindow", "125"))
        self.label_21.setText(_translate("MainWindow", "Dim."))
        self.label_22.setText(_translate("MainWindow", "Samples"))
        self.pcaSamplesLineEdit_s1.setText(_translate("MainWindow", "10000"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Select files"))
        self.btnLoadReference.setText(_translate("MainWindow", "Reference dir"))
        self.btnLoadTest.setText(_translate("MainWindow", "Test dir"))
        self.btnLoadGroungTruth.setText(_translate("MainWindow", "Ground truth"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Run"))
        self.btnCreateDB.setText(_translate("MainWindow", "Create DB"))
        self.btnRecognition.setText(_translate("MainWindow", "Recognition"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Monospace\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p></body></html>"))
        self.outputGroupBox.setTitle(_translate("MainWindow", "Recognized"))
        self.referenceGroupBox.setTitle(_translate("MainWindow", "Ground truth"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Controls"))
        self.btnPause.setText(_translate("MainWindow", "Pause"))
        self.btnStop.setText(_translate("MainWindow", "Stop"))
        self.stage2_groupBox.setTitle(_translate("MainWindow", "STAGE II "))
        self.groupBox_10.setTitle(_translate("MainWindow", "Image size"))
        self.imageWidthLineEdit_s2.setText(_translate("MainWindow", "224"))
        self.imageHeightLineEdit_s2.setText(_translate("MainWindow", "224"))
        self.label_8.setText(_translate("MainWindow", "Width"))
        self.label_9.setText(_translate("MainWindow", "Height"))
        self.label_10.setText(_translate("MainWindow", "px"))
        self.label_13.setText(_translate("MainWindow", "px"))
        self.groupBox_9.setTitle(_translate("MainWindow", "Method"))
        self.vggRadioButton_s2.setText(_translate("MainWindow", "VGG16"))
        self.resnetRadioButton_s2.setText(_translate("MainWindow", "ResNet"))
        self.googlenetRadioButton_s2.setText(_translate("MainWindow", "GoogLeNet"))
        self.groupBox_11.setTitle(_translate("MainWindow", "PCA"))
        self.pcaDimLineEdit_s2.setText(_translate("MainWindow", "100"))
        self.label_23.setText(_translate("MainWindow", "Dim."))
        self.label_24.setText(_translate("MainWindow", "Samples"))
        self.pcaSamplesLineEdit_s2.setText(_translate("MainWindow", "10000"))
        self.groupBox_6.setTitle(_translate("MainWindow", "Output"))
        self.btnSaveOutput.setText(_translate("MainWindow", "Save "))
        self.btnPRcurves.setText(_translate("MainWindow", "PR curves"))
        self.groupBox_12.setTitle(_translate("MainWindow", "Hyperparameters"))
        self.label_17.setText(_translate("MainWindow", "Frame tol."))
        self.frameTolLineEdit.setText(_translate("MainWindow", "2"))
        self.candidatesLineEdit.setText(_translate("MainWindow", "50"))
        self.label_18.setText(_translate("MainWindow", "Candidates"))
        self.prevFramesLineEdit.setText(_translate("MainWindow", "2"))
        self.gpuGroupBox.setTitle(_translate("MainWindow", "GPU Options"))
        self.gpuCandLineEdit.setText(_translate("MainWindow", "2"))
        self.loadDbOnGpuCheckBox.setText(_translate("MainWindow", "Load DB on GPU"))
        self.useGpuCheckBox.setText(_translate("MainWindow", "Use GPU"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen.setText(_translate("MainWindow", "Open Video"))
        self.actionSpectrogram.setText(_translate("MainWindow", "Spectrogram"))
        self.actionFrequency_Map.setText(_translate("MainWindow", "Frequency Map"))
        self.actionSave_path.setText(_translate("MainWindow", "Save to directory"))
        self.actionAbout.setText(_translate("MainWindow", "About"))

