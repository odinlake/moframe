from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel

#from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtWebEngineWidgets import QWebEngineView


class WebWidget(QWidget):
    reverse = False

    def __init__(self, parent, cfg=None):
        QWidget.__init__(self, parent)
        self.config = cfg or {}
        self.setStyleSheet("""
QWidget {
    background: #221111;
    font-weight: bold;
}
        """)
        self.browser = QWebEngineView()
        self.browser.setUrl(QtCore.QUrl(cfg["web-url"]))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)

    def stop(self):
        """
        Stop the gallery widget.
        """
        pass

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        pass

