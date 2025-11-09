from typing import Any, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QSizePolicy, QLabel, 
    QScrollArea, QVBoxLayout
)

from uab.frontend.preview import Preview


class Browser(QWidget):
    """
    Styled Browser widget for preview grid/list and mini-details panel.

    Displays a grid of Preview widgets representing assets with modern styling.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Apply main styling
        self.setStyleSheet("""
            Browser {
                background-color: #1e1e1e;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area to contain the grid
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Container widget for the grid
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)
        
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(15)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Set the container as the scroll area widget
        self.scroll_area.setWidget(self.grid_container)
        
        main_layout.addWidget(self.scroll_area)
        
        self._previews: List[Preview] = []  # keep references and allow introspection

    def _clear_grid(self) -> None:
        """Remove all widgets from the grid layout."""
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        
        # Reset stretch factors
        for i in range(self.grid.columnCount()):
            self.grid.setColumnStretch(i, 0)
        for i in range(self.grid.rowCount()):
            self.grid.setRowStretch(i, 0)

    def draw_previews(self, previews: List[Preview]) -> None:
        """
        Render a set of preview items (thumbnails + names).

        Args:
            previews: List of Preview widgets to display in the grid
        """
        self._clear_grid()
        self._previews = list(previews or [])

        if not self._previews:
            # Show styled empty state message
            empty_container = QWidget()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_icon = QLabel("📁")
            empty_icon.setStyleSheet("font-size: 64pt;")
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_label = QLabel("No assets to display")
            empty_label.setStyleSheet("""
                QLabel {
                    color: #808080;
                    font-size: 16pt;
                    font-weight: 500;
                    padding: 10px;
                }
            """)
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_sublabel = QLabel("Select a folder from the tree to view assets")
            empty_sublabel.setStyleSheet("""
                QLabel {
                    color: #606060;
                    font-size: 11pt;
                    padding: 5px;
                }
            """)
            empty_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_layout.addStretch()
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_label)
            empty_layout.addWidget(empty_sublabel)
            empty_layout.addStretch()
            
            self.grid.addWidget(empty_container, 0, 0, 1, -1)
            return

        # Calculate columns based on available width
        # TODO: fix these magic numbers
        # cols = max(1, (self.width() - 40) // 140)
        # if cols == 0:
        #     cols = 4  # Fallback
        cols = 5
        
        row, col = 0, 0

        for preview in self._previews:
            if isinstance(preview, QWidget):
                preview.setSizePolicy(
                    QSizePolicy.Policy.Fixed,
                    QSizePolicy.Policy.Fixed,
                )
                self.grid.addWidget(preview, row, col, Qt.AlignmentFlag.AlignTop)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1

        # Add stretch to fill remaining space
        if col < cols and col > 0:
            self.grid.setColumnStretch(cols, 1)
        self.grid.setRowStretch(row + 1, 1)
