from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QComboBox, QLabel, QSizePolicy, QPushButton
)
from PySide6.QtGui import QIcon


class Toolbar(QWidget):
    """
    Toolbar widget containing main user controls.
    """

    searchTextChanged = Signal(str)  # Emits search text when it changes
    filterChanged = Signal(str)  # Emits selected filter when it changes
    importClicked = Signal()
    scanClicked = Signal()
    logViewerClicked = Signal()
    rendererChanged = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._init_ui()
        self._apply_style()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMaximumHeight(50)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)

        # Scan Asset Directory button
        self.btn_scan = QPushButton("Scan Asset Directory")
        self.btn_scan.setToolTip("Scan asset directory for new assets")
        self.btn_scan.clicked.connect(self._scan_clicked)

        # Log Viewer button (icon only)
        self.btn_log_viewer = QPushButton()
        self.btn_log_viewer.setToolTip("View Logs")
        self.btn_log_viewer.setFixedSize(36, 36)
        self.btn_log_viewer.clicked.connect(self._log_viewer_clicked)
        self._set_log_icon()

        # Search bar
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #e0e0e0; font-weight: 500;")

        self.search_bar = QLineEdit()
        self.search_bar.setToolTip("Search assets by name, tag, or type...")
        self.search_bar.setPlaceholderText("Search assets by name, tag, or type...")
        self.search_bar.setMinimumWidth(250)
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._on_search_changed)

        # Filter combo box
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("color: #e0e0e0; font-weight: 500;")

        self.filter_combo = QComboBox()
        self.filter_combo.setToolTip("Filter assets by type...")
        self.filter_combo.setMinimumWidth(150)
        self.filter_combo.addItems([
            "All Assets",
            "HDRIs",
            "Textures",
            "Models",
            "Materials",
            "Recent",
            "Favorites"
        ])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)

        renderer_label = QLabel("Renderer:")
        renderer_label.setStyleSheet("color: #e0e0e0; font-weight: 500;")
        # Preferred renderer combo box
        self.cb_renderer = QComboBox()
        self.cb_renderer.setToolTip("Set your preferred renderer.")
        self.cb_renderer.setMinimumWidth(150)
        self.cb_renderer.currentTextChanged.connect(self._on_renderer_changed)

        # Import button
        self.btn_import = QPushButton("Import")
        self.btn_import.clicked.connect(self._on_import_clicked)

        # Add widgets to layout
        # layout.addWidget(self.btn_scan)
        # layout.addWidget(self.btn_log_viewer)
        layout.addWidget(search_label)
        layout.addWidget(self.search_bar, 1)  # Stretch factor 1
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_combo)
        layout.addWidget(renderer_label)
        layout.addWidget(self.cb_renderer)
        layout.addWidget(self.btn_import)
        layout.addStretch()

    def _set_log_icon(self):
        """Set the icon for the log viewer button using Unicode or create a simple icon."""
        # Use a document/list icon as text
        self.btn_log_viewer.setText("≡")
        self.btn_log_viewer.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                font-size: 32pt;
                padding-bottom: 4px;
            }
            QPushButton:hover {
                border: 2px solid #4d4d4d;
                background-color: #2d2d2d;
            }
            QPushButton:pressed {
                background-color: #3d3d3d;
            }
        """)

    def show_import_button(self):
        """Show the import button."""
        self.btn_import.setVisible(True)

    def hide_import_button(self):
        """Hide the import button."""
        self.btn_import.setVisible(False)

    def _scan_clicked(self):
        self.scanClicked.emit()

    def _log_viewer_clicked(self):
        """Handle log viewer button click."""
        self.logViewerClicked.emit()

    def _apply_style(self):
        """Apply styling to the toolbar and its components."""
        self.setStyleSheet("""
            Toolbar {
                background-color: #2d2d2d;
                border-bottom: 2px solid #3d3d3d;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
            }
            QLineEdit:hover {
                border: 2px solid #4d4d4d;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border: 2px solid #4d4d4d;
            }
            QComboBox:focus {
                border: 2px solid #4a9eff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #e0e0e0;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 2px solid #3d3d3d;
                border-radius: 6px;
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #3d3d3d;
            }
        """)

    def _on_search_changed(self, text: str):
        """Handle search text changes."""
        self.searchTextChanged.emit(text)

    def _on_filter_changed(self, text: str):
        """Handle filter selection changes."""
        self.filterChanged.emit(text)

    def get_search_text(self) -> str:
        """
        Get the current search text.

        Returns:
            Current text in the search bar
        """
        return self.search_bar.text()

    def get_selected_filter(self) -> str:
        """
        Get the currently selected filter.

        Returns:
            Current filter selection
        """
        return self.filter_combo.currentText()

    def set_search_text(self, text: str):
        """
        Set the search bar text.

        Args:
            text: Text to set in the search bar
        """
        self.search_bar.setText(text)

    def set_filter(self, filter_text: str):
        """
        Set the selected filter.

        Args:
            filter_text: Filter to select
        """
        index = self.filter_combo.findText(filter_text)
        if index >= 0:
            self.filter_combo.setCurrentIndex(index)

    def add_filter_option(self, option: str):
        """
        Add a new filter option to the combo box.

        Args:
            option: Filter option to add
        """
        if self.filter_combo.findText(option) == -1:
            self.filter_combo.addItem(option)

    def set_allowed_renderers(self, renderers: list[str]):
        for renderer in renderers:
            self.cb_renderer.addItem(renderer)

    def _on_renderer_changed(self, text: str):
        self.rendererChanged.emit(text)

    def clear_search(self):
        """Clear the search bar."""
        self.search_bar.clear()

    def _on_import_clicked(self):
        """Handle import button click."""
        self.importClicked.emit()
