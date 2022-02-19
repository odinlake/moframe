from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush

class ImageWidget(QWidget):
    image = None
    darkenBy = 0x00

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
        img = self.image.getQImage() if self.image else None
        qp = QPainter()
        qp.begin(self)
        if img:
            w, h = self.width(), self.height()
            #img = img.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatioByExpanding)
            imw, imh = img.width(), img.height()
            ix = max(0, (imw - w) / 2)
            iy = max(0, (imh - h) / 2)
            qp.drawImage(0, 0, img, ix, iy)
            brush1 = QBrush(QColor(0x00, 0x00, 0x00, self.darkenBy), Qt.SolidPattern)
            qp.fillRect(0, 0, w, h, brush1)
        else:
            qp.setPen(QColor(168, 34, 3))
            qp.setFont(QFont('Decorative', 10))
            qp.drawText(event.rect(), Qt.AlignCenter, "nothing to show...")
        qp.end()


