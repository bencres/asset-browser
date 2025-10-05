from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget


class Preview(QWidget):
    """
    Skeleton Preview widget representing a single asset preview.
    """

    asset_clicked = Signal(object)         # Emits the asset payload
    asset_double_clicked = Signal(object)   # Emits the asset payload

    def __init__(
        self,
        thumbnail: Optional[QPixmap] = None,
        asset_name: str = "",
        asset_id: Optional[int] = None,
        asset: Optional[Any] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.thumbnail: QPixmap = thumbnail or QPixmap()
        self.asset_name: str = asset_name
        self.asset_id: Optional[int] = asset_id
        self._asset: Optional[Any] = asset

    # Optional helpers to wire events later
    def mousePressEvent(self, event):	
        if event.button() == Qt.MouseButton.LeftButton:
            self.asset_clicked.emit(self._asset)
    
    def mouseDoubleClickEvent(self, event):	
        if event.button() == Qt.MouseButton.LeftButton:
            self.asset_double_clicked.emit(self._asset)
