import sys
import os
import os.path
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from moframe.moframe import MOFrameWindow
import hjson
import importlib.util


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
    mocommands = None

    for path in sys.path:
        cfgpath = os.path.join(path, "..", "moconfig.hjson")
        if os.path.isfile(cfgpath):
            with open(cfgpath, "r") as fh:
                cfg = hjson.load(fh)
        cmdpath = os.path.join(path, "..", "mocommands.py")
        if os.path.isfile(cmdpath):
            spec = importlib.util.spec_from_file_location("mocommands", cmdpath)
            mocommands = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mocommands)

    app = QtWidgets.QApplication(sys.argv)
    app.setOverrideCursor(Qt.BlankCursor)
    #app.changeOverrideCursor(Qt.BlankCursor)
    mainwin = MOFrameWindow(cfg=cfg, cmd=mocommands)
    mainwin.showMaximized()
    MAINWIN = mainwin
    app.installEventFilter(mainwin)
    sys.exit(app.exec_())






















































