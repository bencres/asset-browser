from typing import Any, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QStackedWidget,
)
from uab.core.presenter import Presenter
from uab.frontend.browser import Browser
from uab.frontend.detail import Detail
from uab.frontend.preview import Preview
from uab.frontend.toolbar import Toolbar
from uab.frontend.mini_detail import MiniDetail
from uab.frontend.status_bar import StatusBar


class MainWidget(QWidget):
    """
    Central widget containing the full UI layout of the Universal Asset Browser.
    """

    search_text_changed = Signal(str)
    filter_changed = Signal(str)
    renderer_changed = Signal(str)
    import_clicked = Signal(str)
    scan_clicked = Signal()
    delete_asset_clicked = Signal(int)
    spawn_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_asset = None
        self.current_previews = []

        # Root layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar at top
        self.toolbar = Toolbar()
        self.toolbar.search_text_changed.connect(self._on_search_changed)
        self.toolbar.filter_changed.connect(self._on_filter_changed)
        self.layout.addWidget(self.toolbar)

        # === Main Splitter ===
        self.main_splitter = QSplitter()

        # Stacked (browser/detail/log)
        self.stacked = QStackedWidget()
        self.browser = Browser()
        self.detail = Detail()
        self.stacked.addWidget(self.browser)
        self.stacked.addWidget(self.detail)
        self.main_splitter.addWidget(self.stacked)

        # Mini detail (right)
        self.mini_detail = MiniDetail()
        self.main_splitter.addWidget(self.mini_detail)

        # Configure split sizes, collapsibility
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, True)
        self.main_splitter.setSizes([1200, 0])

        self.layout.addWidget(self.main_splitter)

        # Status bar at bottom
        self.status_bar = StatusBar()
        self.layout.addWidget(self.status_bar)

        self.status_bar.setStyleSheet(self.status_bar.styleSheet())
        self.status_bar.update()

        # --- Connections ---
        self.detail.back_clicked.connect(self.show_browser)
        self.detail.delete_clicked.connect(self._on_delete_asset_clicked)
        self.toolbar.import_asset_selected.connect(self._on_import_clicked)
        self.toolbar.scan_clicked.connect(self._on_scan_clicked)
        self.toolbar.renderer_changed.connect(self._on_renderer_changed)
        self.mini_detail.close_clicked.connect(self.hide_mini_detail)

        self.is_showing_mini_detail = False

        # This GUI's Presenter
        self.presenter = Presenter(self)

    def show_browser(self) -> None:
        self.stacked.setCurrentWidget(self.browser)

    def show_asset_detail(self, asset: dict) -> None:
        self.hide_mini_detail()
        self.stacked.setCurrentWidget(self.detail)
        self.detail.draw_details(asset)

    def toggle_mini_detail(self, asset) -> None:
        if self.is_showing_mini_detail:
            self.hide_mini_detail()
        else:
            self.show_mini_detail(asset)
        self.is_showing_mini_detail = not self.is_showing_mini_detail

    def show_mini_detail(self, asset: dict) -> None:
        if self.stacked.currentWidget() != self.browser:
            return
        self.mini_detail.show_asset(asset)
        sizes = self.main_splitter.sizes()
        if sizes[1] == 0:
            total = sum(sizes)
            self.main_splitter.setSizes(
                [int(total * 0.75), int(total * 0.25)]
            )

    def hide_mini_detail(self) -> None:
        sizes = self.main_splitter.sizes()
        if sizes[1] > 0:
            self.main_splitter.setSizes([sizes[0] + sizes[1], 0])

    def show_message(
        self, msg: str, message_type: str = "info", timeout: int = 5000
    ) -> None:
        self.status_bar.show_message(msg, message_type, timeout)

    def _on_search_changed(self, text: str) -> None:
        self.hide_mini_detail()
        self.search_text_changed.emit(text)

    def _on_filter_changed(self, filter_text: str) -> None:
        self.filter_changed.emit(filter_text)

    def _on_renderer_changed(self, renderer_text: str) -> None:
        self.renderer_changed.emit(renderer_text)

    def _on_import_clicked(self, asset_path: str) -> None:
        self.import_clicked.emit(asset_path)

    def _on_scan_clicked(self) -> None:
        self.scan_clicked.emit()

    def _on_delete_asset_clicked(self, asset_id: int) -> None:
        self.delete_asset_clicked.emit(asset_id)

    def set_current_asset(self, asset: dict) -> None:
        self.current_asset = asset

    def draw_previews(self, previews: list[Preview]) -> None:
        self.current_previews = previews
        self.browser.refresh_previews(previews)

    def set_new_selected_preview(self, preview: Preview) -> Preview:
        if preview.is_selected:
            preview.set_selected(False)
            return preview
        for p in self.current_previews:
            if not p.asset_id == preview.asset_id:
                p.set_selected(False)
            else:
                p.set_selected(True)
        return preview
