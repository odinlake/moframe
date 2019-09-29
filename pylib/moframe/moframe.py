from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QSize, Qt, QTimer

from moframe.imagemodel import ImageModel
from moframe.moimage import MOImage


class MOFrameWindow(QMainWindow):
    reverse = False

    def __init__(self, cfg=None):
        QMainWindow.__init__(self)
        self.config = cfg or {}
        self.setWindowTitle("MOFrame")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
QWidget {
    background: #221111;
    font-weight: bold;
}
        """)

        self.imagemodel = ImageModel(cfg.get("photos-basepath", "."))
        self.imagemodel.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(cfg.get("photos-delay", 1.0) * 1000)

        self.topwidget = QWidget(self)
        self.setCentralWidget(self.topwidget)
        self.photoframe = MOImage(self.topwidget)
        self.helptext = QLabel("Press Escape to Quit", self.topwidget)
        self.helptext.setAlignment(QtCore.Qt.AlignCenter)

        layout = QVBoxLayout(self.topwidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.helptext)
        layout.addWidget(self.photoframe)


    def update(self):
        """
        Update display as needed.
        """
        img = None
        if self.imagemodel.idx == -1 and not self.reverse:
            root, filename, img = self.imagemodel.nextImage()
        elif self.reverse:
            root, filename, img = self.imagemodel.prevImage()
            if not self.imagemodel.hasPrevImage():
                self.reverse = False
                self.imagemodel.idx = -1
        if img:
            self.helptext.hide()
            self.photoframe.setImage(img)
            self.photoframe.show()

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        self.helptext.hide()
        self.photoframe.show()

        if event.key() == QtCore.Qt.Key_Escape:
            self.imagemodel.active = False
            self.imagemodel.join()
            self.close()
        elif event.key() == QtCore.Qt.Key_Space:
            if self.windowState() & Qt.WindowMinimized:
                self.setWindowState(Qt.WindowMaximized)
            else:
                self.setMaximumSize(0, 0)
                self.setWindowState(Qt.WindowMinimized)
        elif event.key() == QtCore.Qt.Key_Left:
            root, filename, img = self.imagemodel.prevImage()
            self.photoframe.setImage(img)
        elif event.key() == QtCore.Qt.Key_Right:
            root, filename, img = self.imagemodel.nextImage()
            self.photoframe.setImage(img)
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.imagemodel.idx = -1
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.reverse = not self.reverse

    def showEvent(self, event):
        """
        When window is shown/restored, make sure it is in fullscreen mode.

        Args:
            event: Qt event.
        """
        self.showFullScreen()
        print("window size:", self.width(), self.height())

