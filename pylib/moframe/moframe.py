from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QSize, Qt, QTimer

from moframe.imagemodel import ImageModel
from moframe.moimage import MOImage


class MOFrameWindow(QMainWindow):
    def __init__(self, cfg=None):
        QMainWindow.__init__(self)
        self.config = cfg or {}
        self.setWindowTitle("MOFrame")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
QWidget {
    background: #8888ff;
    border-width: 5px;
    border-color: red;
}
        """)

        self.imagemodel = ImageModel(cfg.get("photos-basepath", "."))
        self.imagemodel.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

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
        root, filename, img = self.imagemodel.nextImage()
        self.helptext.hide()
        self.photoframe.setImage(img)
        self.photoframe.show()

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.imagemodel.active = False
            self.imagemodel.join()
            self.close()
        if event.key() == QtCore.Qt.Key_Space:
            if self.windowState() & Qt.WindowMinimized:
                self.setWindowState(Qt.WindowMaximized)
            else:
                self.setMaximumSize(0, 0)
                self.setWindowState(Qt.WindowMinimized)

    def showEvent(self, event):
        """
        When window is shown/restored, make sure it is in fullscreen mode.

        Args:
            event: Qt event.
        """
        self.showFullScreen()
        print("window size:", self.width(), self.height())

