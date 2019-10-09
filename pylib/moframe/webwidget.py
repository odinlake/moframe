from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    USING_WEBKIT = False
except ImportError:
    from PyQt5.QtWebKitWidgets import QWebView
    USING_WEBKIT = True

from moframe.basewidget import BaseWidget


class WebWidget(BaseWidget):
    def __init__(self, parent, cfg=None):
        QWidget.__init__(self, parent)
        self.config = cfg or {}
        self.setStyleSheet("""
QWidget {
    background: #221111;
    font-weight: bold;
}
        """)
        if USING_WEBKIT:
            self.browser = QWebView(self)
        else:
            self.browser = QWebEngineView(self)
        self.browser.setUrl(QtCore.QUrl(cfg["web-url"]))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)

    def buttonName(self):
        """
        Returns: String representing a name suitable for a button.
        """
        return "Web\n" + self.config.get("title", "...")

