from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class FileIconWidget(QWidget):
    def __init__(self, pixmap: QPixmap, text: str):
        super().__init__()
        self.setStyleSheet("background-color: #222222;")
        if len(text) > 14:
            text = text[:11] + "..."
        else:
            text = text[:13]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        label_icon = QLabel()
        label_icon.setPixmap(
            pixmap.scaled(
                96,
                96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_text = QLabel(text)
        label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_text.setWordWrap(True)

        layout.addWidget(label_icon)
        layout.addWidget(label_text)

