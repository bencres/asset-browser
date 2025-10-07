from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame


class StatusBar(QFrame):
    """Status bar widget for displaying system messages and notifications."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_style = """
            QLabel#statusBarMessage {
                color: #FFFFFF;
                font-size: 12pt;
                padding: 2px;
                background-color: transparent;
                border: none;
            }
        """
        
        # Set frame shape for better styling control
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Set object name for stylesheet targeting
        self.setObjectName("statusBar")

        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)

        # Message label with unique object name
        self.message_label = QLabel()
        self.message_label.setObjectName("statusBarMessage")
        layout.addWidget(self.message_label, 1)  # Stretch factor

        # Set fixed height
        self.setFixedHeight(28)
        
        # Apply styles
        self._apply_styles()

        # Timer for auto-clearing messages
        self._clear_timer = QTimer(self)
        self._clear_timer.timeout.connect(self.clear)

    def _apply_styles(self):
        self.setStyleSheet("""
            QFrame#statusBar {
                background-color: #141414;
                border-top: 2px solid #4a4a4a;
                border-radius: 0px;
            }
            QLabel#statusBarMessage {
                background-color: transparent;
                color: #FFFFFF;
                font-size: 12pt;
                padding: 2px;
                border: none;
            }
        """)

    def show_message(self, message: str, message_type: str = "info", timeout: int = 0):
        """Display a message in the status bar.

        Args:
            message: The message to display
            message_type: Type of message ('info', 'warning', 'error', 'success')
            timeout: Time in milliseconds before message clears (0 = no auto-clear)
        """
        # Color mapping
        colors = {
            "info": "#FFFFFF",      # White
            "warning": "#FFA500",   # Orange
            "error": "#FF4444",     # Red
            "success": "#44FF44"    # Green
        }
        
        color = colors.get(message_type, "#FFFFFF")
        
        self.message_label.setStyleSheet(f"""
            QLabel#statusBarMessage {{
                color: {color};
                font-size: 12pt;
                padding: 2px;
                background-color: transparent;
                border: none;
            }}
        """)
        self.message_label.setText(message)

        # Handle auto-clear
        if timeout > 0:
            self._clear_timer.start(timeout)
        else:
            self._clear_timer.stop()

    def clear(self):
        """Clear the current status message."""
        self._clear_timer.stop()
        self.message_label.setText("")
        # Reset to default style
        self.message_label.setStyleSheet(self.default_style)
