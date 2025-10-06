from typing import Any, List, Optional

from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QLabel, QScrollArea

from frontend.Preview import Preview


class Browser(QWidget):
    """
    Browser widget for preview grid/list and mini-details panel.

    Displays a grid of Preview widgets representing assets.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Create scroll area to contain the grid
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Container widget for the grid
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(1)
        self.grid.setContentsMargins(1, 1, 1, 1)

        # Set the container as the scroll area widget
        self.scroll_area.setWidget(self.grid_container)

        # Main layout
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
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
            # Show empty state message
            empty_label = QLabel("No assets to display")
            empty_label.setStyleSheet("color: gray; font-size: 14px;")
            self.grid.addWidget(empty_label, 0, 0)
            return

        cols = 8
        row, col = 0, 0

        for preview in self._previews:
            if isinstance(preview, QWidget):
                preview.setSizePolicy(
                    QSizePolicy.Policy.Fixed,
                    QSizePolicy.Policy.Fixed,
                )
                self.grid.addWidget(preview, row, col)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1

        # Add stretch to fill remaining space
        if col < cols:
            self.grid.setColumnStretch(col, 1)
        self.grid.setRowStretch(row + 1, 1)

    def draw_mini_details(self, a: Any) -> None:
        """Render a lightweight details view for the given asset."""
        # TODO: Update a sidebar/area with minimal details.
        pass