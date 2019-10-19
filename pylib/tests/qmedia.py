import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt


from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys


def main():
    """
    An entrypoint.
    """
    media = QUrl.fromLocalFile("D:\\PhotoFrame\\animated\\2019.10.14-romania.busteni.gif")

    app = QtWidgets.QApplication(sys.argv)
    mainwin = QWidget()
    mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
    videoWidget = QVideoWidget()

    layout = QVBoxLayout(mainwin)
    layout.addWidget(videoWidget)

    mediaPlayer.setVideoOutput(videoWidget)
    mediaPlayer.setMedia(QMediaContent(media))
    mediaPlayer.play()

    mainwin.show()
    sys.exit( app.exec_() )






















































