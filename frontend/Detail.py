from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


class Detail(QWidget):
    """
    Skeleton Detail widget for full asset details and metadata editing.
    """

    import_clicked = Signal(object)  # Emits the asset payload

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    def draw_details(self, a: Any) -> None:
        """Draw the full details view for the given asset."""
        # TODO: Populate controls for name, preview, metadata, actions, etc.
        pass

    def display_metadata(self, a: Any) -> None:
        """Display metadata for the given asset without entering edit mode."""
        # TODO: Fill metadata fields in read-only mode.
        pass

    def edit_metadata(self, a: Any) -> None:
        """Enter edit mode for the asset metadata."""
        # TODO: Enable editors for metadata fields.
        pass

    def save_metadata_changes(self, a: Any) -> None:
        """Persist changes to metadata and exit edit mode."""
        # TODO: Validate and emit actions to save through a controller/presenter.
        pass