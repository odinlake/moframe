import sys
import os
import os.path
from PyQt5 import QtWidgets
from moframe.moframe import MOFrameWindow
import json


def main():
    """
    An entrypoint.
    """
    cfg = {}

    for path in sys.path:
        cfgpath = os.path.join(path, "..", "config.json")
        if os.path.isfile(cfgpath):
            with open(cfgpath, "r") as fh:
                cfg = json.load(fh)

    app = QtWidgets.QApplication(sys.argv)
    mainWin = MOFrameWindow(cfg)
    mainWin.showMaximized()
    sys.exit( app.exec_() )






















































