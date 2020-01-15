from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import QSize, Qt, QTimer, QEvent


class MOFrameButton(QPushButton):
    def __init__(self, parent, idx):
        super().__init__(parent)
        self.parent = parent
        self.idx = idx
        if idx == -1:
            self.setText("close\nmenu")
            self.clicked.connect(lambda: self.parent.parent.hideMenu())
        else:
            self.setText(parent.widgets()[idx].buttonName())
            self.clicked.connect(lambda: self.parent.parent.setWidget(self.idx))

        # style background doesn't work on rpi
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(20, 10, 10))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.update()

    def minimumSizeHint(self):
        return QSize(0, 100)

    def maximumSizeHint(self):
        return QSize(300, 250)

    def paintEvent(self, event):
        """
        Custom paint because buttons don't style correctly on RPi.

        Args:
            event: Qt event.
        """
        qp = QtGui.QPainter()
        qp.begin(self)
        w, h = self.width(), self.height()
        brush1 = QtGui.QBrush(QtGui.QColor(0x00, 0x00, 0x00, 0xaa), Qt.SolidPattern)
        brush2 = QtGui.QBrush(QtGui.QColor(0xaa, 0x00, 0x00, 0xff), Qt.Dense7Pattern)
        qp.fillRect(0, 0, w, h, brush1)
        qp.fillRect(0, 0, w, h, brush2)
        qp.drawText(0, 0, w, h, Qt.AlignCenter | Qt.AlignVCenter, self.text())
        qp.setPen(QtGui.QColor(0xff, 0xff, 0xff, 0x88))
        qp.drawRect(0, 0, w-1, h-1)
        qp.end()



class MOFrameMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        for idx, ww in enumerate(parent.central_widgets):
            button = MOFrameButton(self, idx)
            layout.addWidget(button)
        layout.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        button = MOFrameButton(self, -1)
        layout.addWidget(button)

        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, Qt.red)
        self.setPalette(palette)
        self.setGeometry(100, 100, 300, 500)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)

    def widgets(self):
        """
        Returns: List of widgets to make buttons for.
        """
        return self.parent.central_widgets

    def timeout(self):
        """
        USed to hide the menu after some seconds of inactivity.
        """
        self.parent.hideMenu()

    def paintEvent(self, event):
        """
        Image is rescaled to cover frame as snugly as possible, then drawn centered.

        Args:
            event: Qt event.
        """
        qp = QtGui.QPainter()
        qp.begin(self)
        w, h = self.width(), self.height()
        brush1 = QtGui.QBrush(QtGui.QColor(0xaa, 0xaa, 0xaa, 0x88), Qt.SolidPattern)
        brush2 = QtGui.QBrush(QtGui.QColor(0xaa, 0x00, 0x00, 0xff), Qt.Dense7Pattern)
        qp.fillRect(0, 0, w, h, brush1)
        qp.fillRect(0, 0, w, h, brush2)
        qp.end()


class MOFrameWindow(QMainWindow):
    reverse = False

    def __init__(self, cfg=None):
        QMainWindow.__init__(self)
        self.config = cfg or {}
        cfg.setdefault("menu-button-font", "30px bold sans-serif")

        self.setWindowTitle("MOFrame")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
QWidget {
    background: #221111;
    font-weight: bold;
}
QPushButton {
    font: %s;
    color: #ffeeee;
}
        """ % (cfg["menu-button-font"]))
        self.central_widgets = []

        for widget_config in cfg.get("widgets", []):
            if widget_config["type"] == "Gallery":
                from moframe.gallerywidget import GalleryWidget
                ww = GalleryWidget(self, cfg=widget_config)
            elif widget_config["type"] == "Web":
                from moframe.webwidget import WebWidget
                ww = WebWidget(self, cfg=widget_config)
            elif widget_config["type"] == "Camera":
                from moframe.camerawidget import CameraWidget
                ww = CameraWidget(self, cfg=widget_config)
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
                ww.pause()
                ww.hide()
        self.widgetindex = idx
        self.central_widgets[idx].show()
        self.central_widgets[idx].start()
        self.hideMenu()

    def showMenu(self):
        """
        Display the menu and start its timeout.
        """
        app = QtWidgets.QApplication.instance()
        self.menu.show()
        self.menu.timer.start(self.config.get("menu-delay", 5000.0))
        app.setOverrideCursor(Qt.ArrowCursor)

    def hideMenu(self):
        """
        Hide the menu.
        """
        app = QtWidgets.QApplication.instance()
        self.menu.hide()
        app.setOverrideCursor(Qt.BlankCursor)

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
            self.showMenu()
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

