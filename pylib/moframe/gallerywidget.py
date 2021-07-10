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
        self.imagemodel = GalleryModel(cfg)
        self.imagemodel.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.photoframe = ImageWidget(self)
        self.movieframe = QLabel(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.photoframe)
        layout.addWidget(self.movieframe)
        self.delayMultiplier = 1000.0

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
        if self.reverse:
            root, filename, img = self.imagemodel.prevImage()
            if not self.imagemodel.hasPrevImage():
                self.reverse = False
                self.imagemodel.idx = -1
        else:
            root, filename, img = self.imagemodel.nextImage()
        if img:
            if img.contents == "image":
                self.photoframe.setImage(img)
                self.movieframe.hide()
                self.photoframe.show()
            elif img.contents == "animation":
                img.unload()
                movie = img.getQMovie()
                self.movieframe.setMovie(movie)
                movie.start()
                self.photoframe.hide()
                self.movieframe.show()
            self.timer.setInterval(self.getDelay())

    def getDelay(self):
        return self.config.get("photos-delay", 1.0) * self.delayMultiplier

    def start(self):
        """
        Start or resume widget.
        """
        self.imagemodel.paused = False
        self.timer.start(100)

    def pause(self):
        """
        Temporarily stop the widget from updating.
        """
        self.imagemodel.paused = True
        self.timer.stop()

    def stop(self):
        """
        Stop the gallery widget.
        """
        self.pause()
        self.imagemodel.active = False
        self.imagemodel.join()

    def next(self):
        """
        Handle "next" command if applicable.
        """
        root, filename, img = self.imagemodel.nextImage()
        self.photoframe.setImage(img)

    def previous(self):
        """
        Handle "previous" command if applicable.
        """
        root, filename, img = self.imagemodel.prevImage()
        self.photoframe.setImage(img)

    def faster(self):
        """
        Handle "faster" command if applicable.
        """
        if self.delayMultiplier > 1:
            self.delayMultiplier /= 5.0
        self.start()

    def slower(self):
        """
        Handle "slower" command if applicable.
        """
        if self.delayMultiplier < 10e6:
            self.delayMultiplier *= 5.0
        self.start()

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        self.photoframe.show()
        if event.key() == QtCore.Qt.Key_Left:
            self.previous()
        elif event.key() == QtCore.Qt.Key_Right:
            self.next()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.imagemodel.idx = -1
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.reverse = not self.reverse

    def getStatus(self):
        """
        Return status information as a dictionary.
        """
        return {
            "speed": "%s" % (60000.0 / self.getDelay()),
            "speed-unit": "photos per minute",
            "current-image-idx": "{} of {}".format(
                self.imagemodel.getCurrentImageIndexForward(),
                len(self.imagemodel.history),
            ),
            "current-image-name": self.imagemodel.getCurrentImageKey()[1],
        }















