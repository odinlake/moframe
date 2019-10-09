from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QImage, QPainter, QColor, QFont

import cv2

from moframe.basewidget import BaseWidget


class CameraWidget(BaseWidget):
    image = None

    def __init__(self, parent, cfg=None):
        QWidget.__init__(self, parent)
        self.config = cfg or {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.vc = cv2.VideoCapture(cfg.get("camera-index", 0))

    def update(self):
        """
        Update display as needed.
        """
        rval, frame = self.vc.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.setImage(image)

    def setImage(self, img):
        """
        Change which image is displayed.

        Args:
            img (QImage): A valid image to display.
        """
        self.image = img
        self.repaint()

    def paintEvent(self, event):
        """
        Image is rescaled to cover frame as snugly as possible, then drawn centered.

        Args:
            event: Qt event.
        """
        qp = QPainter()
        qp.begin(self)
        if self.image:
            w, h = self.width(), self.height()
            img = self.image.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatioByExpanding)
            imw, imh = img.width(), img.height()
            ix = max(0, (imw - w) / 2)
            iy = max(0, (imh - h) / 2)
            qp.drawImage(0, 0, img, ix, iy)
        else:
            qp.setPen(QColor(168, 34, 3))
            qp.setFont(QFont('Decorative', 10))
            qp.drawText(event.rect(), Qt.AlignCenter, "nothing to show...")
        qp.end()

    def buttonName(self):
        """
        Returns: String representing a name suitable for a button.
        """
        return "Camera\n" + self.config.get("title", "...")


    def start(self):
        """
        Start or resume widget.
        """
        self.timer.start(self.config.get("camera-delay", 0.1) * 1000)

    def pause(self):
        """
        Temporarily stop the widget from updating.
        """
        self.timer.stop()

    def stop(self):
        """
        Stop the widget terminally.
        """
        self.pause()

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        pass

