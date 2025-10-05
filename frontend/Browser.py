from __future__ import annotations

from typing import Any, List, Optional

from PySide6.QtWidgets import QWidget


class Browser(QWidget):
    """
    Skeleton Browser widget for preview grid/list and mini-details panel.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    def draw_previews(self, previews: List[Any]) -> None:
        """Render a set of preview items (thumbnails + names)."""
        # TODO: Populate layout with Preview widgets.
        pass

    def draw_mini_details(self, a: Any) -> None:
        """Render a lightweight details view for the given asset."""
        # TODO: Update a sidebar/area with minimal details.
        pass