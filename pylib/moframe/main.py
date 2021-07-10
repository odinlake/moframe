import sys
import os
import os.path
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from moframe.moframe import MOFrameWindow
import hjson


MAINWIN = None

# skywriter is too noisy and unreliable
"""
try:
    import skywriter
except ImportError:
    skywriter = None

if skywriter:
    @skywriter.move()
    def skywriterMove(x, y, z):
        if MAINWIN:
            MAINWIN.skywriterQueue.append(("move", x, y, z))
"""


def main():
    """
    An entrypoint.
    """
    global MAINWIN
    cfg = {}

    for path in sys.path:
        cfgpath = os.path.join(path, "..", "moconfig.hjson")
        if os.path.isfile(cfgpath):
            with open(cfgpath, "r") as fh:
                cfg = hjson.load(fh)

    app = QtWidgets.QApplication(sys.argv)
    app.setOverrideCursor(Qt.BlankCursor)
    #app.changeOverrideCursor(Qt.BlankCursor)
    mainwin = MOFrameWindow(cfg=cfg)
    mainwin.showMaximized()
    MAINWIN = mainwin
    app.installEventFilter(mainwin)
    sys.exit(app.exec_())






















































