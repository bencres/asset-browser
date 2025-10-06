from typing import Any

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSplitter, QStackedWidget
from frontend.Browser import Browser
from frontend.Detail import Detail
from frontend.Toolbar import Toolbar
from frontend.Tree import Tree


class Window(QMainWindow):
    """
    Skeleton view class generated from mermaid UML.

    Responsibilities:
    - Acts as the View in an MVC/MVP architecture.
    - Receives a Presenter (or Controller) via bindEvents and exposes UI callbacks.
    - Rendering and widget wiring should be implemented in concrete code later.
    """

    # Signal to notify presenter of tree item selection
    treeItemSelected = Signal(str)
    searchTextChanged = Signal(str)
    filterChanged = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self.resize(800, 600)

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.splitter = QSplitter()

        self.toolbar = Toolbar()
        self.toolbar.searchTextChanged.connect(self._on_search_changed)
        self.toolbar.filterChanged.connect(self._on_filter_changed)
        self.layout.addWidget(self.toolbar)

        self.tree = Tree()
        self.stacked = QStackedWidget()
        self.browser = Browser()
        self.detail = Detail()
        self.stacked.addWidget(self.browser)
        self.stacked.addWidget(self.detail)
        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.stacked)
        self.splitter.setSizes([150, 650])

        self.layout.addWidget(self.splitter)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Connect tree's signal to window's signal
        self.tree.treeItemClicked.connect(self._on_tree_item_clicked)
        self.detail.back_clicked.connect(self.show_browser)

    def show_browser(self) -> None:
        """Show the browser view."""
        self.stacked.setCurrentWidget(self.browser)

    def show_asset_detail(self, asset: dict) -> None:
        """Show the detail view for the given asset."""
        self.stacked.setCurrentWidget(self.detail)
        self.detail.draw_details(asset)

    def _on_tree_item_clicked(self, path: str) -> None:
        """Internal handler that forwards tree clicks to presenter via signal."""
        self.treeItemSelected.emit(path)

    # UML: + showMessage(msg)
    def show_message(self, msg: str) -> None:
        """Display a message to the user."""
        # TODO: Implement message display (e.g., status bar or message box)
        pass

    # UML: + bindEvents(presenter: Presenter)
    # def bind_events(self, presenter: Any) -> None:
    #     """Bind a presenter/controller to this view."""
    #     # Connect Window's signal to Presenter's handler
    #     self.treeItemSelected.connect(self.presenter.on_tree_item_clicked)

    # UML: + onBackClicked(w: QWidget)
    def onBackClicked(self, w: QWidget) -> None:  # type: ignore[name-defined]
        """Handle back navigation from a given widget."""
        pass

    # UML: + onImportClicked(a: Asset)
    def onImportClicked(self, a: Any) -> None:
        """Handle importing the given asset."""
        pass

    # UML: + onTreeItemClicked(i: TreeItem)
    def onTreeItemClicked(self, i: Any) -> None:
        """Handle clicks on a tree item representing a directory or asset."""
        pass

    # UML: + onValidateDatabaseClicked(a: Asset)
    def onValidateDatabaseClicked(self, a: Any) -> None:
        """Trigger database validation for the given asset or scope."""
        pass

    # UML: + onEditMetadata(a: Asset)
    def onEditMetadata(self, a: Any) -> None:
        """Enter an edit mode for asset metadata."""
        pass

    # UML: + onSaveMetadataChanges(a: Asset)
    def onSaveMetadataChanges(self, a: Any) -> None:
        """Persist metadata changes for the given asset."""
        pass

    def _on_search_changed(self, text: str):
        """Handle search text changes."""
        self.searchTextChanged.emit(text)

    def _on_filter_changed(self, text: str):
        self.filterChanged.emit(text)
