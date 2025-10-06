from typing import Any, Optional

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect


class Preview(QWidget):
    """
    Styled Preview widget representing a single asset preview.

    Features:
    - Hover effects
    - Shadow on hover
    - Rounded corners
    - Professional styling
    """

    asset_clicked = Signal(int)
    asset_double_clicked = Signal(int)

    def __init__(
        self,
        thumbnail: Optional[QPixmap] = None,
        asset_name: str = "",
        asset_id: int = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.thumbnail: QPixmap = thumbnail or QPixmap()
        self.asset_name: str = asset_name
        self.asset_id: Optional[int] = asset_id
        self._is_hovered = False

        # Set fixed size for the preview widget
        self.setFixedSize(QSize(180, 220))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Apply initial styling
        self._apply_style(hovered=False)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Image container with background
        self.image_container = QWidget()
        self.image_container.setFixedSize(160, 160)
        self.image_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #333333;
            }
        """)

        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)

        # Icon label
        self.label_icon = QLabel()
        if not self.thumbnail.isNull():
            scaled_pixmap = self.thumbnail.scaled(
                156,
                156,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.label_icon.setPixmap(scaled_pixmap)
        else:
            # Placeholder for missing image
            self.label_icon.setText("No Preview")
            self.label_icon.setStyleSheet("color: #666666; font-size: 11pt;")

        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.label_icon)

        # Text label
        self.label_text = QLabel(self.asset_name)
        self.label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_text.setWordWrap(True)
        self.label_text.setMaximumHeight(40)
        self.label_text.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 11pt;
                font-weight: 500;
                background: transparent;
                padding: 2px;
            }
        """)

        # Add widgets to layout
        layout.addWidget(self.image_container)
        layout.addWidget(self.label_text)
        layout.addStretch()

        # Add shadow effect (will be shown on hover)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 150, 255, 180))
        self.shadow.setOffset(0, 0)
        self.shadow.setEnabled(False)
        self.setGraphicsEffect(self.shadow)

    def _apply_style(self, hovered: bool = False, clicked: bool = False):
        """Apply styling based on hover state."""
        if hovered or clicked:
            self.setStyleSheet("""
                Preview {
                    background-color: #2d2d2d;
                    border: 2px solid #4a9eff;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                Preview {
                    background-color: #242424;
                    border: 2px solid #333333;
                    border-radius: 12px;
                }
            """)

    def enterEvent(self, event):
        """Handle mouse enter event."""
        self._is_hovered = True
        self._apply_style(hovered=True)
        self.shadow.setEnabled(True)

        # Update image container border on hover
        self.image_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #4a9eff;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self._is_hovered = False
        self._apply_style(hovered=False)
        self.shadow.setEnabled(False)

        # Reset image container border
        self.image_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #333333;
            }
        """)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.asset_clicked.emit(self.asset_id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.asset_double_clicked.emit(self.asset_id)
        super().mouseDoubleClickEvent(event)
