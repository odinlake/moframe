import sys
from PyQt5 import QtWidgets
from moframe.moframe import MOFrameWindow


def main():
    """
    An entrypoint.
    """
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MOFrameWindow()
    mainWin.showMaximized() # showMaximized
    sys.exit( app.exec_() )






















































