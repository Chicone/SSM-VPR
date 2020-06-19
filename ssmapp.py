#import simpler as signalgen
import ssm
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap

import time

# class ControlMainWindow(QtGui.QMainWindow):
class ControlMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = ssm.ssm_MainWindow()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pixmap = QPixmap("intro_small.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    time.sleep(0.1)
    app.processEvents()
    time.sleep(.5)
    # splash.finish(0)
    mySW = ControlMainWindow()
    mySW.show()
    splash.finish(mySW)
    sys.exit(app.exec_())