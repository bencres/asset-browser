from typing import Optional
from PySide6.QtCore import Qt, QSize, QEvent, Signal
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
)


class Preview(QWidget):
    """
    Responsive Preview widget representing a single asset preview.

    - Scales dynamically with grid cell size.
    - Hides text & info button when too small.
    - Maintains hover/selection styling without layout breaking.
    """

    # Signals your browser already expects
    show_mini_details = Signal(int)
    asset_clicked = Signal(int)
    asset_double_clicked = Signal(int)

    def __init__(
        self,
        asset_id: int,
        thumbnail: Optional[QPixmap] = None,
        asset_name: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.asset_id = asset_id
        self.asset_name = asset_name
        self.thumbnail: QPixmap = thumbnail or QPixmap()
        self.is_selected = False
        self._hover = False

        # --------------------------
        # Core styling
        # --------------------------
        self.setStyleSheet("""
            Preview {
                background-color: #242424;
                border: 2px solid #333333;
                border-radius: 10px;
            }
        """)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        # --------------------------
        # Layout structure
        # --------------------------
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(4, 4, 4, 4)
        self.vlayout.setSpacing(2)

        # --- image container ---
        self.image_container = QWidget()
        self.image_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.image_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 6px;
                border: 2px solid #333333;
            }
        """)
        self.image_container.installEventFilter(self)
        self.vlayout.addWidget(self.image_container, 1)

        # shadow for selection
        self.shadow = QGraphicsDropShadowEffect(blurRadius=20)
        self.shadow.setColor(QColor(0, 150, 255, 180))
        self.shadow.setOffset(0, 0)
        self.shadow.setEnabled(False)
        self.image_container.setGraphicsEffect(self.shadow)

        # image label
        img_layout = QVBoxLayout(self.image_container)
        img_layout.setContentsMargins(0, 0, 0, 0)
        self.label_icon = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_icon.setScaledContents(False)
        img_layout.addWidget(self.label_icon)

        # --- text/info row ---
        self.text_container = QWidget()
        self.text_container.setSizePolicy(QSizePolicy.Policy.Preferred,
                                          QSizePolicy.Policy.Minimum)
        self.text_container.setStyleSheet("background: transparent;")

        text_layout = QHBoxLayout(self.text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)

        self.label_text = QLabel(self.asset_name)
        self.label_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_text.setWordWrap(True)
        self.label_text.setStyleSheet("""
            QLabel {
                color: #e0e0e0; font-size: 10pt;
                background: transparent;
            }
        """)

        self.info_button = QPushButton("i")
        self.info_button.setFixedSize(14, 14)
        self.info_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_button.setToolTip("Show asset details")
        self.info_button.clicked.connect(self._on_info_clicked)
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #595959;
                font-size: 9pt;
                border-radius: 6px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #4a9eff; color: white;
            }
        """)

        text_layout.addStretch(1)
        text_layout.addWidget(self.label_text)
        text_layout.addWidget(self.info_button)
        text_layout.addStretch(1)

        self.vlayout.addWidget(self.text_container)

        # setup image contents
        self._update_pixmap_display()

    # ------------------------------------------------------------------
    # Reactions
    # ------------------------------------------------------------------

    def eventFilter(self, obj, ev):
        if obj == self.image_container:
            if ev.type() == QEvent.Type.Enter:
                self._hover = True
                self._update_style()
            elif ev.type() == QEvent.Type.Leave:
                self._hover = False
                self._update_style()
        return super().eventFilter(obj, ev)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.image_container.geometry().contains(e.pos()):
                self.asset_clicked.emit(self.asset_id)
        super().mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            if self.image_container.geometry().contains(e.pos()):
                self.asset_double_clicked.emit(self.asset_id)
        super().mouseDoubleClickEvent(e)

    # ------------------------------------------------------------------
    # Style and behavior helpers
    # ------------------------------------------------------------------

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self._update_style()

    def _update_style(self):
        if self.is_selected:
            # selected state
            self.setStyleSheet("""
                Preview {
                    background-color: #2a2a2a;
                    border: 2px solid #4a9eff;
                    border-radius: 10px;
                }
            """)
            self.image_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border: 2px solid #4a9eff;
                    border-radius: 6px;
                }
            """)
            self.shadow.setEnabled(True)
        elif self._hover:
            self.setStyleSheet("""
                Preview {
                    background-color: #2d2d2d;
                    border: 2px solid #506680;
                    border-radius: 10px;
                }
            """)
            self.image_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border: 2px solid #506680;
                    border-radius: 6px;
                }
            """)
            self.shadow.setEnabled(False)
        else:
            # normal
            self.setStyleSheet("""
                Preview {
                    background-color: #242424;
                    border: 2px solid #333333;
                    border-radius: 10px;
                }
            """)
            self.image_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border: 2px solid #333333;
                    border-radius: 6px;
                }
            """)
            self.shadow.setEnabled(False)

    def _on_info_clicked(self):
        self.show_mini_details.emit(self.asset_id)

    # ------------------------------------------------------------------
    # Resize / scaling
    # ------------------------------------------------------------------

    def resizeEvent(self, e):
        """Scale thumbnail & adapt subview visibility when grid shrinks."""
        super().resizeEvent(e)
        self._update_pixmap_display()

        # Hide text/info when cell becomes tiny — prevent overlap
        h = self.height()
        if h < 80:
            self.text_container.hide()
        else:
            self.text_container.show()

    def _update_pixmap_display(self):
        """Recompute icon scaling for current container size."""
        if self.thumbnail.isNull():
            self.label_icon.setText("No Preview")
            self.label_icon.setStyleSheet(
                "color:#666; font-size:9pt; background:transparent;"
            )
            self.label_icon.setPixmap(QPixmap())
            return

        size = self.image_container.size()
        if size.width() < 1 or size.height() < 1:
            return

        scaled = self.thumbnail.scaled(
            size.width() - 6,
            size.height() - 6,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.label_icon.setPixmap(scaled)
