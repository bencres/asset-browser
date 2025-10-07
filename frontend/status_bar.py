from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class StatusBar(QWidget):
    """Status bar widget for displaying system messages and notifications."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Message label
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
                padding: 2px;
            }
        """)
        layout.addWidget(self.message_label)

        # Set fixed height
        self.setFixedHeight(32)
        self.setStyleSheet("""
            StatusBar {
                background-color: #2d2d2d;
                border-top: 1px solid #3d3d3d;
            }
        """)

        # Timer for auto-clearing messages
        self._clear_timer = QTimer(self)
        self._clear_timer.timeout.connect(self.clear)

    def show_message(self, message: str, message_type: str = "info", timeout: int = 0):
        """Display a message in the status bar.

        Args:
            message: The message to display
            message_type: Type of message ('info', 'warning', 'error', 'success')
            timeout: Time in milliseconds before message clears (0 = no auto-clear)
        """
        # Style based on message type
        style = "QLabel { color: "
        if message_type == "warning":
            style += "#FFA500;"  # Orange
        elif message_type == "error":
            style += "#FF4444;"  # Red
        elif message_type == "success":
            style += "#44FF44;"  # Green
        else:  # info
            style += "#FFFFFF;"  # White
        style += " }"

        self.message_label.setStyleSheet(style)
        self.message_label.setText(message)

        # Handle auto-clear
        if timeout > 0:
            self._clear_timer.start(timeout)

    def clear(self):
        """Clear the current status message."""
        self._clear_timer.stop()
        self.message_label.setText("")
        self.message_label.setStyleSheet("")
