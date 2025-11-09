from typing import Any

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
from uab.frontend.tree import Tree
from uab.frontend.toolbar import Toolbar
from uab.frontend.mini_detail import MiniDetail
from uab.frontend.status_bar import StatusBar


class MainWidget(QWidget):
    """
    Central widget containing the full UI layout of the Universal Asset Browser.
    """

    # Signals to forward from this central widget
    treeItemSelected = Signal(str)
    searchTextChanged = Signal(str)
    filterChanged = Signal(str)
    rendererChanged = Signal(str)
    importClicked = Signal(str)
    scanClicked = Signal()
    logViewerClicked = Signal()
    deleteAssetClicked = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Root layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar at top
        self.toolbar = Toolbar()
        self.toolbar.searchTextChanged.connect(self._on_search_changed)
        self.toolbar.filterChanged.connect(self._on_filter_changed)
        self.layout.addWidget(self.toolbar)

        # === Main Splitter ===
        self.main_splitter = QSplitter()

        # Tree (left)
        self.tree = Tree()
        self.main_splitter.addWidget(self.tree)

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
        self.main_splitter.setCollapsible(0, True)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setCollapsible(2, True)
        self.main_splitter.setSizes([0, 1200, 0])

        self.layout.addWidget(self.main_splitter)

        # Status bar at bottom
        self.status_bar = StatusBar()
        self.layout.addWidget(self.status_bar)

        self.status_bar.setStyleSheet(self.status_bar.styleSheet())
        self.status_bar.update()

        # --- Connections ---
        self.tree.treeItemClicked.connect(self._on_tree_item_clicked)
        self.detail.back_clicked.connect(self.show_browser)
        self.detail.delete_clicked.connect(self._on_delete_asset_clicked)
        self.toolbar.importAssetSelected.connect(self._on_import_clicked)
        self.toolbar.scanClicked.connect(self._on_scan_clicked)
        self.toolbar.rendererChanged.connect(self._on_renderer_changed)
        self.mini_detail.closeClicked.connect(self.hide_mini_detail)

        self.is_showing_mini_detail = False

        # This GUI's Presenter
        self.presenter = Presenter(self)

    # === Core UI Logic ===

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
        if sizes[2] == 0:
            total = sum(sizes)
            self.main_splitter.setSizes(
                [int(total * 0.0), int(total * 0.75), int(total * 0.25)]
            )

    def hide_mini_detail(self) -> None:
        sizes = self.main_splitter.sizes()
        if sizes[2] > 0:
            self.main_splitter.setSizes([sizes[0], sizes[1] + sizes[2], 0])

    def show_message(
        self, msg: str, message_type: str = "info", timeout: int = 5000
    ) -> None:
        self.status_bar.show_message(msg, message_type, timeout)

    # === Signal Handlers ===

    def _on_tree_item_clicked(self, path: str) -> None:
        self.hide_mini_detail()
        self.treeItemSelected.emit(path)

    def _on_search_changed(self, text: str) -> None:
        self.hide_mini_detail()
        self.searchTextChanged.emit(text)

    def _on_filter_changed(self, filter_text: str) -> None:
        self.filterChanged.emit(filter_text)

    def _on_renderer_changed(self, renderer_text: str) -> None:
        self.rendererChanged.emit(renderer_text)

    def _on_import_clicked(self, asset_path: str) -> None:
        self.importClicked.emit(asset_path)

    def _on_scan_clicked(self) -> None:
        self.scanClicked.emit()


    def _on_delete_asset_clicked(self, asset_id: int) -> None:
        self.deleteAssetClicked.emit(asset_id)
