from typing import Any, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QScrollArea,
    QFrame, QSizePolicy
)


class Detail(QWidget):
    """
    Detail widget for full asset details and metadata editing.

    Displays:
    - Preview image (read-only)
    - Name (editable)
    - File path (editable)
    - Description (editable)
    - Tags (editable)
    """

    back_clicked = Signal()
    save_clicked = Signal(dict)  # Emits the updated asset data
    delete_clicked = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.current_asset: Optional[dict] = None
        self.is_edit_mode: bool = False

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Top buttons (Back, Edit, Save, Import)
        button_layout = QHBoxLayout()

        self.btn_back = QPushButton("← Back")
        self.btn_back.setToolTip("Back to asset list")
        self.btn_back.setMaximumWidth(100)
        self.btn_back.clicked.connect(self._on_back_clicked)

        button_layout.addWidget(self.btn_back)
        button_layout.addStretch()

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setToolTip("Edit asset metadata")
        self.btn_edit.setMaximumWidth(100)
        self.btn_edit.clicked.connect(self._on_edit_clicked)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setToolTip("Remove asset from library (does not delete the file on your machine)")
        self.btn_delete.setMaximumWidth(100)
        self.btn_delete.clicked.connect(self._on_delete_clicked)

        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save changes to asset metadata")
        self.btn_save.setMaximumWidth(100)
        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_save.setVisible(False)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setToolTip("Cancel changes and return to asset list")
        self.btn_cancel.setMaximumWidth(100)
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        self.btn_cancel.setVisible(False)

        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)

        content_layout.addLayout(button_layout)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(separator1)

        # Preview Image
        preview_container = QHBoxLayout()
        preview_container.addStretch()

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setMaximumSize(500, 500)
        self.preview_label.setScaledContents(False)
        self.preview_label.setStyleSheet("border: 1px solid #555; background-color: #1a1a1a;")

        preview_container.addWidget(self.preview_label)
        preview_container.addStretch()
        content_layout.addLayout(preview_container)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(separator2)

        # Name field
        name_layout = QVBoxLayout()
        name_label = QLabel("Name:")
        name_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.name_display = QLabel()
        self.name_display.setWordWrap(True)
        self.name_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.name_edit = QLineEdit()
        self.name_edit.setVisible(False)

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_display)
        name_layout.addWidget(self.name_edit)
        content_layout.addLayout(name_layout)

        # File Path field
        path_layout = QVBoxLayout()
        path_label = QLabel("File Path:")
        path_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.path_display = QLabel()
        self.path_display.setWordWrap(True)
        self.path_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.path_display.setStyleSheet("color: #888;")

        self.path_edit = QLineEdit()
        self.path_edit.setVisible(False)

        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_display)
        path_layout.addWidget(self.path_edit)
        content_layout.addLayout(path_layout)

        # Description field
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.desc_display = QLabel()
        self.desc_display.setWordWrap(True)
        self.desc_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.desc_display.setMinimumHeight(60)

        self.desc_edit = QTextEdit()
        self.desc_edit.setVisible(False)
        self.desc_edit.setMaximumHeight(150)

        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_display)
        desc_layout.addWidget(self.desc_edit)
        content_layout.addLayout(desc_layout)

        # Tags field
        tags_layout = QVBoxLayout()
        tags_label = QLabel("Tags:")
        tags_label.setStyleSheet("font-weight: bold; font-size: 16pt;")
        self.tags_display = QLabel()
        self.tags_display.setWordWrap(True)
        self.tags_display.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.tags_edit = QLineEdit()
        self.tags_edit.setVisible(False)
        self.tags_edit.setPlaceholderText("Enter tags separated by commas")

        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_display)
        tags_layout.addWidget(self.tags_edit)
        content_layout.addLayout(tags_layout)

        # Add stretch at the bottom
        content_layout.addStretch()

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def draw_details(self, asset: dict) -> None:
        """
        Draw the full details view for the given asset.

        Args:
            asset: Dictionary containing asset data with keys:
                   name, directory_path, description, tags, id, preview_image_file_path
        """
        self.current_asset = asset
        self.display_metadata(asset)
        self._set_edit_mode(False)

    def display_metadata(self, asset: dict) -> None:
        """
        Display metadata for the given asset without entering edit mode.

        Args:
            asset: Dictionary containing asset data
        """
        if not asset:
            return

        # Load and display preview image
        preview_path = asset.get('preview_image_file_path') or asset.get('directory_path', '')
        if preview_path:
            # Try to load preview from directory
            import os
            dir_path = preview_path if os.path.isdir(preview_path) else asset.get('directory_path', '')

            if dir_path:
                # Normalize path
                norm = os.path.normpath(dir_path)
                if not norm.startswith(os.sep):
                    norm = os.sep + norm

                # Try to find preview file
                preview_file = None
                for ext in ['.png', '.webp', '.jpg', '.jpeg']:
                    candidate = os.path.join(norm, 'preview' + ext)
                    if os.path.isfile(candidate):
                        preview_file = candidate
                        break

                if preview_file:
                    pixmap = QPixmap(preview_file)
                    if not pixmap.isNull():
                        # Scale the pixmap to fit the label while maintaining aspect ratio
                        scaled_pixmap = pixmap.scaled(
                            self.preview_label.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.preview_label.setPixmap(scaled_pixmap)
                    else:
                        self.preview_label.setText("Preview not available")
                else:
                    self.preview_label.setText("Preview not available")
            else:
                self.preview_label.setText("Preview not available")
        else:
            self.preview_label.setText("Preview not available")

        # Display name
        name = asset.get('name', 'Unnamed Asset')
        self.name_display.setText(name)
        self.name_edit.setText(name)

        # Display file path
        path = asset.get('directory_path', 'No path specified')
        self.path_display.setText(path)
        self.path_edit.setText(path)

        # Display description
        description = asset.get('description') or 'No description provided'
        self.desc_display.setText(description)
        self.desc_edit.setPlainText(asset.get('description', ''))

        # Display tags
        tags = asset.get('tags', [])
        if isinstance(tags, list):
            tags_str = ', '.join(tags) if tags else 'No tags'
        else:
            tags_str = str(tags) if tags else 'No tags'
        self.tags_display.setText(tags_str)
        self.tags_edit.setText(', '.join(tags) if isinstance(tags, list) else str(tags))

    def edit_metadata(self, asset: dict) -> None:
        """
        Enter edit mode for the asset metadata.

        Args:
            asset: Dictionary containing asset data
        """
        self.current_asset = asset
        self.display_metadata(asset)
        self._set_edit_mode(True)

    def save_metadata_changes(self) -> dict:
        """
        Collect the edited metadata and prepare it for saving.

        Returns:
            Dictionary with updated asset data
        """
        if not self.current_asset:
            return {}

        # Collect the edited values
        updated_asset = dict(self.current_asset)
        updated_asset['name'] = self.name_edit.text()
        updated_asset['directory_path'] = self.path_edit.text()
        updated_asset['description'] = self.desc_edit.toPlainText()

        # Parse tags
        tags_text = self.tags_edit.text()
        if tags_text:
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            updated_asset['tags'] = tags
        else:
            updated_asset['tags'] = []

        return updated_asset

    def _set_edit_mode(self, edit_mode: bool) -> None:
        """
        Toggle between display and edit mode.

        Args:
            edit_mode: True to enable editing, False to disable
        """
        self.is_edit_mode = edit_mode

        # Toggle visibility of display vs edit widgets
        self.name_display.setVisible(not edit_mode)
        self.name_edit.setVisible(edit_mode)

        self.path_display.setVisible(not edit_mode)
        self.path_edit.setVisible(edit_mode)

        self.desc_display.setVisible(not edit_mode)
        self.desc_edit.setVisible(edit_mode)

        self.tags_display.setVisible(not edit_mode)
        self.tags_edit.setVisible(edit_mode)

        # Toggle button visibility
        self.btn_edit.setVisible(not edit_mode)
        self.btn_save.setVisible(edit_mode)
        self.btn_cancel.setVisible(edit_mode)

    def _on_back_clicked(self) -> None:
        """Handle back button click."""
        self.back_clicked.emit()

    def _on_delete_clicked(self) -> None:
        self.delete_clicked.emit(self.current_asset['id'] if self.current_asset else -1)

    def _on_edit_clicked(self) -> None:
        """Handle edit button click."""
        if self.current_asset:
            self.edit_metadata(self.current_asset)

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        updated_asset = self.save_metadata_changes()
        if updated_asset:
            # Update the display with the new values
            self.display_metadata(updated_asset)
            self._set_edit_mode(False)
            # Emit signal with updated asset
            self.save_clicked.emit(updated_asset)

    def _on_cancel_clicked(self) -> None:
        """Handle cancel button click."""
        # Restore original values
        if self.current_asset:
            self.display_metadata(self.current_asset)
        self._set_edit_mode(False)
