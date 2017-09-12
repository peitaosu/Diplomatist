import sys
from PyQt4 import QtCore, QtGui, uic
qt_ui_file = "diplomatist.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_ui_file)

class Diplomatist_Qt(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    diplomatist_ui = Diplomatist_Qt()
    #diplomatist_ui.setWindowFlags(QtCore.Qt.Tool)
    diplomatist_ui.show()
    sys.exit(app.exec_())