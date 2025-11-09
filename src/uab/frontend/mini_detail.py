from typing import Optional
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
)


class MiniDetail(QWidget):
    """
    Mini detail widget showing a compact view of asset information.

    Displays:
    - Preview image
    - Asset name
    - Tags

    This view appears in the splitter when a preview is clicked.
    """

    close_clicked = Signal()  # Emitted when close button is clicked

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.current_asset: Optional[dict] = None
        self._init_ui()
        self._apply_style()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(12)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header with title and close button
        header_layout = QHBoxLayout()

        title_label = QLabel("Asset Info")
        title_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14pt;
                font-weight: bold;
                padding-bottom: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Close button with X icon
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self._on_close_clicked)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888888;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 4px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #4a9eff;
                color: #ffffff;
            }
        """)
        header_layout.addWidget(self.btn_close)

        content_layout.addLayout(header_layout)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        separator1.setStyleSheet("background-color: #3d3d3d;")
        content_layout.addWidget(separator1)

        # Preview Image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setMaximumSize(300, 300)
        self.preview_label.setScaledContents(False)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                background-color: #1a1a1a;
                padding: 10px;
            }
        """)
        content_layout.addWidget(self.preview_label)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("background-color: #3d3d3d;")
        content_layout.addWidget(separator2)

        # Name section
        name_title = QLabel("Name")
        name_title.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 10pt;
                font-weight: bold;
                padding-top: 5px;
            }
        """)
        content_layout.addWidget(name_title)

        self.name_label = QLabel()
        self.name_label.setWordWrap(True)
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 11pt;
                padding: 5px;
                background-color: #2a2a2a;
                border-radius: 4px;
            }
        """)
        content_layout.addWidget(self.name_label)

        # Tags section
        tags_title = QLabel("Tags")
        tags_title.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 10pt;
                font-weight: bold;
                padding-top: 10px;
            }
        """)
        content_layout.addWidget(tags_title)

        self.tags_label = QLabel()
        self.tags_label.setWordWrap(True)
        self.tags_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.tags_label.setStyleSheet("""
            QLabel {
                color: #a0a0a0;
                font-size: 10pt;
                padding: 8px;
                background-color: #2a2a2a;
                border-radius: 4px;
                font-style: italic;
            }
        """)
        content_layout.addWidget(self.tags_label)

        # Add stretch at bottom
        content_layout.addStretch()

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _apply_style(self):
        """Apply overall styling to the widget."""
        self.setStyleSheet("""
            MiniDetail {
                background-color: #252525;
                border-left: 2px solid #3d3d3d;
            }
            QScrollArea {
                border: none;
                background-color: #252525;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def _on_close_clicked(self):
        """Handle close button click."""
        self.close_clicked.emit()

    def show_asset(self, asset: dict) -> None:
        """
        Display asset information.

        Args:
            asset: Dictionary containing asset data with keys:
                   name, directory_path, tags, id, preview_image_file_path
        """
        self.current_asset = asset

        if not asset:
            self.clear()
            return

        # Load and display preview image
        preview_path = asset.get('preview_image_file_path') or asset.get('directory_path', '')
        pixmap = self._load_preview_image(preview_path, asset.get('directory_path', ''))

        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                280, 280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText("No Preview")
            self.preview_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #3d3d3d;
                    border-radius: 8px;
                    background-color: #1a1a1a;
                    padding: 10px;
                    color: #666666;
                    font-size: 12pt;
                }
            """)

        # Display name
        name = asset.get('name', 'Unnamed Asset')
        self.name_label.setText(name)

        # Display tags
        tags = asset.get('tags', [])
        if isinstance(tags, list) and tags:
            # Create styled tag chips
            tags_html = ' '.join([
                f'<span style="background-color: #3d3d3d; padding: 3px 8px; border-radius: 10px; margin-right: 5px;">{tag}</span>'
                for tag in tags])
            self.tags_label.setText(tags_html)
        elif isinstance(tags, str) and tags:
            self.tags_label.setText(tags)
        else:
            self.tags_label.setText('<i style="color: #666666;">No tags</i>')

    def _load_preview_image(self, preview_path: str, directory_path: str) -> Optional[QPixmap]:
        """
        Load preview image from path.

        Args:
            preview_path: Direct path to preview image
            directory_path: Fallback directory path to search for preview

        Returns:
            QPixmap if found, None otherwise
        """
        if not preview_path and not directory_path:
            return None

        dir_path = preview_path if os.path.isdir(preview_path) else directory_path

        if not dir_path:
            return None

        # Normalize path
        norm = os.path.normpath(dir_path)
        if not norm.startswith(os.sep):
            norm = os.sep + norm

        # Try to find preview file
        for ext in ['.png', '.webp', '.jpg', '.jpeg']:
            candidate = os.path.join(norm, 'preview' + ext)
            if os.path.isfile(candidate):
                pixmap = QPixmap(candidate)
                if not pixmap.isNull():
                    return pixmap

        return None

    def clear(self):
        """Clear the display."""
        self.current_asset = None
        self.preview_label.clear()
        self.preview_label.setText("No asset selected")
        self.name_label.setText("-")
        self.tags_label.setText("-")

    def hide_widget(self):
        """Hide this widget from view."""
        self.hide()

    def show_widget(self):
        """Show this widget."""
        self.show()