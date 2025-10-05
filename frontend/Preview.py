from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class Preview(QWidget):
    """
    Skeleton Preview widget representing a single asset preview.
    """

    asset_clicked = Signal(object)
    asset_double_clicked = Signal(object)

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
        self.setStyleSheet("background-color: #222222;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        label_icon = QLabel()
        label_icon.setPixmap(
            self.thumbnail.scaled(
                96,
                96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_text = QLabel(self.asset_name)
        label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_text.setWordWrap(True)

        layout.addWidget(label_icon)
        layout.addWidget(label_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.asset_clicked.emit(self.asset_id)
    
    def mouseDoubleClickEvent(self, event):	
        if event.button() == Qt.MouseButton.LeftButton:
            self.asset_double_clicked.emit(self.asset_id)
