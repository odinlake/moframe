from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont


class ImageWidget(QWidget):
    image = None

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


