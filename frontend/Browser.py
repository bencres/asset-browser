from __future__ import annotations

from typing import Any, List, Optional

from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy, QLabel

from frontend.Preview import Preview

class Browser(QWidget):
    """
    Skeleton Browser widget for preview grid/list and mini-details panel.
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(1)
        self.grid.setContentsMargins(1, 1, 1, 1)
        self._previews: List[Preview] = []  # keep references and allow introspection

    def _clear_grid(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

    def draw_previews(self, previews: List[Preview]) -> None:
        """Render a set of preview items (thumbnails + names)."""
        for preview in previews:
            print(preview)
        self._clear_grid()
        self._previews = list(previews or [])
        if not self._previews:
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

        if col < cols:
            self.grid.setColumnStretch(col, 1)
        self.grid.setRowStretch(row, 1)


    def draw_mini_details(self, a: Any) -> None:
        """Render a lightweight details view for the given asset."""
        # TODO: Update a sidebar/area with minimal details.
        pass
