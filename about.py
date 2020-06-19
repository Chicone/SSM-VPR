import aboutbase
from PyQt5.QtWidgets import QDialog

class AboutForm(QDialog):
  def __init__(self, parent=None):
     super(AboutForm, self).__init__(parent)
     self.ui = aboutbase.Ui_Dialog()
     self.ui.setupUi(self)
     self.ui.buttonBox.accepted.connect(self.okButtonClicked)
     self.setWindowTitle("SSM-VPR - About")
     self.groupToAdd = None

  def okButtonClicked(self):
     self.close()