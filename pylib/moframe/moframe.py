from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import QSize, Qt, QTimer, QEvent

from moframe.gallerywidget import GalleryWidget
from moframe.webwidget import WebWidget


class MOFrameButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: rgba(255, 240, 240, 0.6);
            font: 40px bold sans-serif;
            color: #221111;
        """)

    def minimumSizeHint(self):
        return QSize(0, 200)

    def maximumSizeHint(self):
        return QSize(300, 300)


class MOFrameMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for idx, ww in enumerate(parent.central_widgets):
            button = MOFrameButton(self)
            button.setText("Widget-%d" % idx)
            layout.addWidget(button)
        layout.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, Qt.red)
        self.setPalette(palette)
        self.setGeometry(100, 100, 300, 500)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)

    def timeout(self):
        """
        USed to hide the menu after some seconds of inactivity.
        """
        self.hide()

    def paintEvent(self, event):
        """
        Image is rescaled to cover frame as snugly as possible, then drawn centered.

        Args:
            event: Qt event.
        """
        qp = QtGui.QPainter()
        qp.begin(self)
        w, h = self.width(), self.height()
        qp.setBrush(Qt.Dense5Pattern)
        qp.setPen(Qt.NoPen)
        qp.fillRect(0, 0, w, h, Qt.Dense5Pattern)
        qp.end()


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
        self.central_widgets = []

        for widget_config in cfg.get("widgets", []):
            if widget_config["type"] == "Gallery":
                ww = GalleryWidget(self, cfg=widget_config)
            elif widget_config["type"] == "Web":
                ww = WebWidget(self, cfg=widget_config)
            self.central_widgets.append(ww)

        self.setCentralWidget(QWidget(self))
        self.menu = MOFrameMenu(self)

        layout = QHBoxLayout(self.centralWidget())
        layout.setContentsMargins(0, 0, 0, 0)
        for ww in self.central_widgets:
            layout.addWidget(ww)

        self.setWidget(0)

    def setWidget(self, idx):
        """
        Choose which widget in the list of central widgets, to display.
        """
        idx = idx % len(self.central_widgets)
        for ii, ww in enumerate(self.central_widgets):
            if ii != idx:
                ww.hide()
        self.widgetindex = idx
        self.central_widgets[idx].show()

    def eventFilter(self, source, event):
        """
        Global event filter that intercepts all keyboard events.
        This should be attached to the QApplication object.

        Args:
            source: widget where the event originated.
            event: qt event object.

        Returns: True iff we intercept the event globally, i.e.,
        it is a keyboard event.
        """
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True
        elif event.type() in (QEvent.MouseMove, QEvent.MouseButtonPress):
            self.menu.show()
            self.menu.timer.start(self.config.get("menu-delay", 5000.0))
        res = super().eventFilter(source, event)
        return res

    def resizeEvent(self, event):
        """
        Update UI when window is resized.

        Args:
            event: Qt event.
        """
        super().resizeEvent(event)
        ww, hh = self.width(), self.height()
        self.menu.setGeometry(ww - 300, 0, 300, hh)

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        self.centralWidget().keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Escape:
            for widget in self.central_widgets:
                widget.stop()
            self.close()
        elif event.key() == QtCore.Qt.Key_Space:
            if self.windowState() & Qt.WindowMinimized:
                self.setWindowState(Qt.WindowMaximized)
            else:
                self.setMaximumSize(0, 0)
                self.setWindowState(Qt.WindowMinimized)
        elif event.key() == QtCore.Qt.Key_PageUp:
            self.setWidget(self.widgetindex + 1)
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.setWidget(self.widgetindex - 1)

    def showEvent(self, event):
        """
        When window is shown/restored, make sure it is in fullscreen mode.

        Args:
            event: Qt event.
        """
        self.showFullScreen()
        print("window size:", self.width(), self.height())

