from typing import Any, Optional

from PySide6.QtCore import Signal, Qt, QSize, QEvent
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QHBoxLayout, QPushButton


class Preview(QWidget):
    """
    Styled Preview widget representing a single asset preview.
    """

    show_mini_details = Signal(int)
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
        self._is_image_hovered = False

        # Set fixed size for the preview widget
        self.setFixedSize(QSize(180, 220))

        # Apply initial styling (no border initially)
        self.setStyleSheet("""
            Preview {
                background-color: #242424;
                border: 2px solid #333333;
                border-radius: 12px;
            }
        """)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Image container with background
        self.image_container = QWidget()
        self.image_container.setFixedSize(160, 160)
        self.image_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #333333;
            }
        """)
        # Install event filter to track mouse hover on image container
        self.image_container.installEventFilter(self)

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

        # Text label container with info button
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;")
        text_layout = QHBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

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

        # Info button
        self.info_button = QPushButton("ℹ")
        self.info_button.setFixedSize(20, 20)
        self.info_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_button.setToolTip("Show asset details")
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #4a9eff;
                border: 1px solid #4a9eff;
                border-radius: 10px;
                font-size: 12pt;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #4a9eff;
                color: #ffffff;
                border: 1px solid #5aa9ff;
            }
            QPushButton:pressed {
                background-color: #3a8eef;
            }
        """)
        self.info_button.clicked.connect(self._on_info_clicked)

        # Add widgets to text layout
        text_layout.addStretch()
        text_layout.addWidget(self.label_text)
        text_layout.addWidget(self.info_button)
        text_layout.addStretch()

        # Add widgets to main layout
        layout.addWidget(self.image_container)
        layout.addWidget(text_container)
        layout.addStretch()

        # Add shadow effect (will be shown on hover)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 150, 255, 180))
        self.shadow.setOffset(0, 0)
        self.shadow.setEnabled(False)
        self.setGraphicsEffect(self.shadow)

    def eventFilter(self, obj, event):
        """Filter events for the image container to detect hover."""
        if obj == self.image_container:
            if event.type() == QEvent.Type.Enter:
                self._on_image_enter()
                return False
            elif event.type() == QEvent.Type.Leave:
                self._on_image_leave()
                return False
        return super().eventFilter(obj, event)

    def _on_image_enter(self):
        """Handle mouse entering the image container."""
        self._is_image_hovered = True
        self._apply_image_hover_style(True)

    def _on_image_leave(self):
        """Handle mouse leaving the image container."""
        self._is_image_hovered = False
        self._apply_image_hover_style(False)

    def _apply_image_hover_style(self, hovered: bool):
        """Apply styling based on image hover state."""
        if hovered:
            # Highlight the entire widget
            self.setStyleSheet("""
                Preview {
                    background-color: #2d2d2d;
                    border: 2px solid #4a9eff;
                    border-radius: 12px;
                }
            """)
            # Highlight the image container border
            self.image_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    border: 2px solid #4a9eff;
                }
            """)
            # Enable shadow effect
            self.shadow.setEnabled(True)
        else:
            # Reset to normal style
            self.setStyleSheet("""
                Preview {
                    background-color: #242424;
                    border: 2px solid #333333;
                    border-radius: 12px;
                }
            """)
            # Reset image container border
            self.image_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    border: 2px solid #333333;
                }
            """)
            # Disable shadow effect
            self.shadow.setEnabled(False)

    def _on_info_clicked(self):
        """Handle info button click."""
        self.show_mini_details.emit(self.asset_id)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click event on the image container."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if the click is within the image container bounds
            if self.image_container.geometry().contains(event.pos()):
                self.asset_double_clicked.emit(self.asset_id)
        super().mouseDoubleClickEvent(event)
