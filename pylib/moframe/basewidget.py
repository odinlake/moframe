from PyQt5.QtWidgets import QWidget


class BaseWidget(QWidget):
    def __init__(self, parent, cfg=None):
        QWidget.__init__(self, parent)
        self.config = cfg or {}

    def buttonName(self):
        """
        Returns: String representing a name suitable for a button connected to
        the widget.
        """
        return "Undefined\n" + self.config.get("title", "...")

    def start(self):
        """
        Start the widget when it is first to be used, or resume from pase.
        """
        pass

    def pause(self):
        """
        Temporarily stop the widget from updating.
        """
        pass

    def stop(self):
        """
        Stop the widget when it is to be destroyed.
        """
        pass

    def keyPressEvent(self, event):
        """
        Handle keyboard commands.

        Args:
            event: Qt event.
        """
        pass

    def next(self):
        """
        Handle "next" command if applicable.
        """
        pass

    def previous(self):
        """
        Handle "previous" command if applicable.
        """
        pass

    def faster(self):
        """
        Handle "faster" command if applicable.
        """
        pass

    def slower(self):
        """
        Handle "slower" command if applicable.
        """
        pass

    def getStatus(self):
        """
        Return status information as a dictionary.
        """
        return {}
