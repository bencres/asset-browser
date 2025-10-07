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
