from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QSize, Qt, QTimer

from moframe.basewidget import BaseWidget
from moframe.gallerymodel import GalleryModel
from moframe.imagewidget import ImageWidget


class GalleryWidget(BaseWidget):
    reverse = False

    def __init__(self, parent, cfg=None):
        QWidget.__init__(self, parent)
        self.config = cfg or {}
        self.imagemodel = GalleryModel(cfg.get("photos-basepath", "."))
        self.imagemodel.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.photoframe = ImageWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.photoframe)

    def buttonName(self):
        """
        Returns: String representing a name suitable for a button.
        """
        return "Gallery\n" + self.config.get("title", "...")

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
            self.photoframe.setImage(img)
            self.photoframe.show()

    def start(self):
        """
        Start or resume widget.
        """
        self.timer.start(self.config.get("photos-delay", 1.0) * 1000)

    def pause(self):
        """
        Temporarily stop the widget from updating.
        """
        self.timer.stop()

    def stop(self):
        """
        Stop the gallery widget.
        """
        self.pause()
        self.imagemodel.active = False
        self.imagemodel.join()

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        self.photoframe.show()
        if event.key() == QtCore.Qt.Key_Left:
            root, filename, img = self.imagemodel.prevImage()
            self.photoframe.setImage(img)
        elif event.key() == QtCore.Qt.Key_Right:
            root, filename, img = self.imagemodel.nextImage()
            self.photoframe.setImage(img)
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.imagemodel.idx = -1
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.reverse = not self.reverse

