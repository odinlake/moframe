from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import QSize, Qt, QTimer, QEvent
from collections import deque
import time


class MOFrameButtonBase(QPushButton):
    def __init__(self, parent, command=None, icon=None):
        super().__init__(parent)
        self.icon = None
        if command:
            self.clicked.connect(command)
        if icon == "light":
            self.icon = QtGui.QIcon('./resource/lightbulb.svg')
        # style background doesn't work on rpi
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(20, 10, 10))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.update()

    def minimumSizeHint(self):
        return QSize(50, 100)

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
        if self.icon:
            self.icon.paint(qp, QtCore.QRect(10, 10, h - 20, h - 20))
        qp.drawText(0, 0, w, h, Qt.AlignCenter | Qt.AlignVCenter, self.text())
        qp.setPen(QtGui.QColor(0xff, 0xff, 0xff, 0x88))
        qp.drawRect(0, 0, w-1, h-1)
        qp.end()


class MOFrameButton(MOFrameButtonBase):
    def __init__(self, parent, idx):
        super().__init__(parent)
        self.parent = parent
        self.idx = idx
        self.setText(parent.widgets()[idx].buttonName())
        self.clicked.connect(lambda: self.parent.parent.setWidget(self.idx))


class MOFrameControlButton(MOFrameButtonBase):
    def __init__(self, parent, text, command, icon=None):
        super().__init__(parent, icon=icon)
        self.parent = parent
        self.setText(text)
        self.clicked.connect(lambda: command(parent.parent))


class MOFrameMenuBase(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, Qt.red)
        self.setPalette(palette)
        self.setGeometry(100, 100, 300, 500)

    def paintEvent(self, event):
        """
        Draw custom menu background as styling doesn't work on the RPi.

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


class MOTimeDisplay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.reftimer = None
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setAutoFillBackground(False)
        self.setStyleSheet("color: #998888; background-color: rgba(0, 0, 0, 128);")
        self.setFont(QtGui.QFont('Arial', 50))
        self.timer = QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.timeout)
        self.setGeometry(100, 100, 500, 70)

    def updateText(self):
        """
        Update text with time left. Hide and stop if none is left.
        """
        if self.reftimer:
            seconds = int(self.reftimer.remainingTime() / 1000.0 + 0.5)
            if seconds > 0:
                if seconds < 5:
                    self.setText("done" + "." * seconds)
                else:
                    hours = seconds // 3600
                    seconds -= hours * 3600
                    minutes = seconds // 60
                    seconds -= minutes * 60
                    self.setText("{}:{}:{} time left".format(hours, minutes, seconds))
            else:
                self.timer.stop()
                self.hide()
                self.reftimer = None

    def timeout(self):
        """
        Used to hide the menu after some seconds of inactivity.
        """
        self.updateText()

    def show(self, reftimer, timeout=200):
        super().show()
        self.reftimer = reftimer
        self.timer.start(timeout)
        self.updateText()


class MOFramePopup(MOFrameMenuBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        layout = QVBoxLayout(self)
        left = QWidget(self)
        right = QWidget(self)
        top = QWidget(self)
        layoutLR = QHBoxLayout(top)
        layoutLR.addWidget(left)
        layoutLR.addWidget(right)

        layout1 = QVBoxLayout(left)
        layout1.setContentsMargins(5, 5, 5, 5)
        layout1.setSpacing(5)
        layout2 = QVBoxLayout(right)
        layout2.setContentsMargins(5, 5, 5, 5)
        layout2.setSpacing(5)

        layout.addWidget(top)
        layout.addWidget(MOFrameControlButton(self, "close menu", self.closeMenu))

        layout1.addWidget(MOFrameControlButton(self, "All lights ON", self.allLightsOn))
        layout1.addWidget(MOFrameControlButton(self, "   ..on for ten seconds", lambda f: self.allLightsOffTimer(10 * 1000)))
        layout1.addWidget(MOFrameControlButton(self, "   ..on for one hour", lambda f: self.allLightsOffTimer(3600.0 * 1000)))
        layout1.addWidget(MOFrameControlButton(self, "   ..on for two hours", lambda f: self.allLightsOffTimer(2 * 3600.0 * 1000)))
        layout1.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        layout2.addWidget(MOFrameControlButton(self, "All lights OFF", self.allLightsOff))
        layout2.addWidget(MOFrameControlButton(self, "   ..off for ten seconds", lambda f: self.allLightsOnTimer(10 * 1000)))
        layout2.addWidget(MOFrameControlButton(self, "   ..off for one hour", lambda f: self.allLightsOnTimer(3600.0 * 1000)))
        layout2.addWidget(MOFrameControlButton(self, "   ..off for two hours", lambda f: self.allLightsOnTimer(2 * 3600.0 * 1000)))
        layout2.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.lightstimer = QTimer(self)
        self.lightstimer.setSingleShot(True)
        self.lightstimer.timeout.connect(self.toggle)

        self.lastLightState = 0  # (-1, 0, 1) = (off, unknown, on)

    def toggle(self):
        """
        """
        if self.lastLightState > 0:
            self.allLightsOff(None)
        elif self.lastLightState < 0:
            self.allLightsOn(None)

    def closeMenu(self, _frame=None):
        """
        """
        self.parent.hideMenu()

    def allLightsOff(self, _frame=None):
        """
        """
        self.closeMenu()
        print(self.parent.customCommand("cmdAllLightsOff"))
        self.lastLightState = -1
        self.lightstimer.stop()

    def allLightsOn(self, _frame=None):
        """
        """
        self.closeMenu()
        print(self.parent.customCommand("cmdAllLightsOn"))
        self.lastLightState = 1
        self.lightstimer.stop()

    def allLightsOnTimer(self, delay=10000.0):
        """
        """
        self.allLightsOff(None)
        self.lightstimer.start(delay)
        self.parent.timedisplay.show(self.lightstimer)

    def allLightsOffTimer(self, delay=10000.0):
        """
        """
        self.allLightsOn(None)
        self.lightstimer.start(delay)
        self.parent.timedisplay.show(self.lightstimer)


class MOFrameMenu(MOFrameMenuBase):
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

        lightsbutton = MOFrameControlButton(self, "lights", self.showLights, icon="light")
        layout.addWidget(lightsbutton)

    def showLights(self, frame):
        """

        :param frame:
        :return:
        """
        self.parent.showPopup()

    def widgets(self):
        """
        Returns: List of widgets to make buttons for.
        """
        return self.parent.central_widgets


class MOFrameControls(MOFrameMenuBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.addWidget(MOFrameControlButton(self, "pause", self.pause))
        layout.addWidget(MOFrameControlButton(self, "resume", self.resume))
        layout.addWidget(MOFrameControlButton(self, "next", self.next))
        layout.addWidget(MOFrameControlButton(self, "previous", self.previous))
        layout.addWidget(MOFrameControlButton(self, "faster", self.faster))
        layout.addWidget(MOFrameControlButton(self, "slower", self.slower))
        layout.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

    def speedText(self):
        s = self.parent.currentWidget().getStatus()
        return "{} {}".format(s.get("speed", ""), s.get("speed-unit", "")) if "speed" in s else ""

    def imageText(self):
        s = self.parent.currentWidget().getStatus()
        return "({}): {}".format(
            s.get("current-image-idx", ""), s.get("current-image-name", "")
        )

    def pause(self, frame):
        frame.currentWidget().pause()
        frame.flashStatus("paused")

    def resume(self, frame):
        frame.currentWidget().start()
        frame.flashStatus("resumed: " + self.speedText())

    def next(self, frame):
        self.pause(frame)
        frame.currentWidget().next()
        frame.flashStatus(self.imageText())

    def previous(self, frame):
        self.pause(frame)
        frame.currentWidget().previous()
        frame.flashStatus(self.imageText())

    def faster(self, frame):
        self.resume(frame)
        frame.currentWidget().faster()
        frame.flashStatus("faster: " + self.speedText())

    def slower(self, frame):
        self.resume(frame)
        frame.currentWidget().slower()
        frame.flashStatus("slower: " + self.speedText())


class MOStatusLabel(QLabel):
    def __init__(self, parent, text=""):
        super().__init__(parent)
        self.parent = parent
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setAutoFillBackground(False)
        self.setFont(QtGui.QFont('Arial', 30))
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)

    def timeout(self):
        """
        Used to hide the menu after some seconds of inactivity.
        """
        self.hide()

    def show(self, timeout=1000):
        super().show()
        self.timer.start(timeout)


class MOFrameWindow(QMainWindow):
    reverse = False

    def __init__(self, cfg=None, cmd=None):
        QMainWindow.__init__(self)
        self.config = cfg or {}
        self.commands = cmd or None
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
QLabel {
    font: "300px bold sans-serif";
    color: #ffeeee;
}
        """ % (cfg["menu-button-font"]))
        self.central_widgets = []
        self.setCentralWidget(QWidget(self))
        centralw = self.centralWidget()

        for widget_config in cfg.get("widgets", []):
            if widget_config["type"] == "Gallery":
                from moframe.gallerywidget import GalleryWidget
                ww = GalleryWidget(centralw, cfg=widget_config)
            elif widget_config["type"] == "Web":
                from moframe.webwidget import WebWidget
                ww = WebWidget(centralw, cfg=widget_config)
            elif widget_config["type"] == "Camera":
                from moframe.camerawidget import CameraWidget
                ww = CameraWidget(centralw, cfg=widget_config)
            else:
                ww = None
            if ww:
                self.central_widgets.append(ww)

        layout = QHBoxLayout(centralw)
        layout.setContentsMargins(0, 0, 0, 0)
        for ww in self.central_widgets:
            layout.addWidget(ww)

        self.menu = MOFrameMenu(self)
        self.controls = MOFrameControls(self)
        self.popupLights = MOFramePopup(self)
        self.closebutton = MOFrameControlButton(self, "close menu", lambda _: self.menutimer.start(0))
        self.timedisplay = MOTimeDisplay(self)

        self.closebutton.hide()
        self.timedisplay.hide()
        self.marker = QPushButton("X", self)
        self.marker.hide()
        self.statusLabel = MOStatusLabel(self, "this is the status text")
        self.statusLabel.hide()
        self.setWidget(0)
        self.utilTimer = QTimer(self)
        self.utilTimer.timeout.connect(self.utilLoop)
        self.utilTimer.start(0.5)
        self.skywriterQueue = deque()
        self.skywriterTimeout = 0
        self.pointer = (0, 0)
        self.widgetindex = 0
        self.setMouseTracking(True)
        self.menutimer = QTimer(self)
        self.menutimer.setSingleShot(True)
        self.menutimer.timeout.connect(self.hideMenu)
        self.hideMenu()
        self.activePopup = None

    def customCommand(self, command):
        """
        """
        if self.commands:
            cmd = getattr(self.commands, command, None)
            if callable(cmd):
                return cmd(self)
        return "undefined: {}".format(command)

    def flashStatus(self, text, timeout=1000):
        """
        Display status text briefly.
        """
        self.statusLabel.setText(text)
        self.statusLabel.show(timeout)

    def utilLoop(self):
        t = self.skywriterTimeout
        if t and time.time() - t > 3.0:
            self.marker.hide()
            self.skywriterTimeout = 0
        while self.skywriterQueue:
            args = self.skywriterQueue.popleft()
            if args[0] == "move":
                self.skywriterMove(*args[1:])
            self.skywriterTimeout = time.time()

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

    def currentWidget(self):
        """
        Get currently active widget among central widgets.
        """
        return self.central_widgets[self.widgetindex]

    def showMenu(self):
        """
        Display the menu and start its timeout.
        """
        if not self.activePopup:
            app = QtWidgets.QApplication.instance()
            app.setOverrideCursor(Qt.ArrowCursor)
            hidedelay = self.config.get("menu-delay", 5000.0)
            self.menu.show()
            self.closebutton.show()
            self.controls.show()
            self.menutimer.start(hidedelay)

    def hideMenu(self):
        """
        Hide the menu.
        """
        app = QtWidgets.QApplication.instance()
        self.menutimer.stop()
        self.menu.hide()
        self.controls.hide()
        self.closebutton.hide()
        self.popupLights.hide()
        app.setOverrideCursor(Qt.BlankCursor)
        self.activePopup = None

    def showPopup(self):
        """
        Show a popup and adjust close timer.
        """
        self.hideMenu()
        app = QtWidgets.QApplication.instance()
        app.setOverrideCursor(Qt.ArrowCursor)
        hidedelay = 5 * self.config.get("menu-delay", 5000.0)
        self.popupLights.show()
        self.menutimer.start(hidedelay)
        self.activePopup = self.popupLights

    def doLater(self, cb, delay=0):
        """
        Do callback cb after delay millisecs. If delay is 0, just do at the end of the
        current event queue.
        """
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(cb)
        timer.start(delay)

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
        res = super().eventFilter(source, event)
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True
        elif event.type() in (QEvent.MouseButtonPress,):
            pt = self.mapFromGlobal(event.globalPos())
            self.pointer = (pt.x(), pt.y())
            self.doLater(self.showMenu)
        elif event.type() in (QEvent.MouseMove,):
            pt = self.mapFromGlobal(event.globalPos())
            self.pointer = (pt.x(), pt.y())
            if pt.x() and pt.y():
                self.skywriterMove(pt.x(), pt.y(), 30)
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
        self.controls.setGeometry(0, 0, 300, hh)
        self.closebutton.setGeometry(ww / 2 - 150, 50, 300, 100)
        self.popupLights.setGeometry(10, 10, ww - 20, hh - 20)
        self.statusLabel.setGeometry(ww * 0.25, hh * 0.8, ww * 0.5, hh * 0.15)

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

    def skywriterMove(self, x, y, z):
        """
        Skywriter API forwarded and handled on qt event loop (do not call on skywriter thread).

        Args:
            x: [0, 1] x coordinate on skyhat
            y: [0, 1] y coordinate on skyhat
            z: [0, 1], higher when hand is close or covers more of skyhat
        """
        ww, hh = self.width(), self.height()
        s = 70 * (1.0 - z)
        self.marker.setGeometry(ww * x, hh * (1.0 - y), 30 + s, 30 + s)
        self.marker.show()

    def setDarkness(self, darkness=0x00):
        """
        :param darkness: 0x00-0xff where 0xff is black
        :return:
        """
        for ww in self.central_widgets:
            if hasattr(ww, "photoframe"):
                ww.photoframe.darkenBy = darkness
                ww.repaint()


