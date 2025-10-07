from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QStackedWidget
from frontend.browser import Browser
from frontend.detail import Detail
from frontend.tree import Tree
from frontend.toolbar import Toolbar
from frontend.mini_detail import MiniDetail
from frontend.log_viewer import LogViewer
from frontend.status_bar import StatusBar


class Window(QMainWindow):
    """
    Main window class for the Universal Asset Browser. View in MVP.
    """

    # Signals
    treeItemSelected = Signal(str)
    searchTextChanged = Signal(str)
    filterChanged = Signal(str)
    importClicked = Signal()
    scanClicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self.resize(1200, 700)

        self.widget = QWidget()
        self.layout = QVBoxLayout()

        # Create and add toolbar at the top
        self.toolbar = Toolbar()
        self.toolbar.searchTextChanged.connect(self._on_search_changed)
        self.toolbar.filterChanged.connect(self._on_filter_changed)
        self.layout.addWidget(self.toolbar)

        # Create main splitter for content area
        self.main_splitter = QSplitter()

        # Left: Tree view
        self.tree = Tree()
        self.main_splitter.addWidget(self.tree)

        # Middle: Browser/Detail stacked widget
        self.stacked = QStackedWidget()
        self.browser = Browser()
        self.detail = Detail()
        self.log_viewer = LogViewer()
        self.stacked.addWidget(self.browser)
        self.stacked.addWidget(self.detail)
        self.stacked.addWidget(self.log_viewer)
        self.main_splitter.addWidget(self.stacked)

        # Right: Mini detail view (initially hidden)
        self.mini_detail = MiniDetail()
        self.main_splitter.addWidget(self.mini_detail)

        # Make the mini detail panel collapsible
        self.main_splitter.setCollapsible(0, False)  # Tree cannot be collapsed
        self.main_splitter.setCollapsible(1, False)  # Browser cannot be collapsed
        self.main_splitter.setCollapsible(2, True)  # Mini detail can be collapsed

        # Set initial splitter sizes [tree, browser, mini_detail]
        # Start with mini detail hidden (size 0)
        self.main_splitter.setSizes([200, 1000, 0])

        self.layout.addWidget(self.main_splitter)

        # Create and add status bar at the bottom
        self.status_bar = StatusBar()
        self.layout.addWidget(self.status_bar)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Connect signals
        self.tree.treeItemClicked.connect(self._on_tree_item_clicked)
        self.detail.back_clicked.connect(self.show_browser)
        self.toolbar.importClicked.connect(self._on_import_clicked)
        self.toolbar.scanClicked.connect(self._on_scan_clicked)
        self.mini_detail.closeClicked.connect(self.hide_mini_detail)
        self.log_viewer.closeRequested.connect(self.show_browser)

    def show_browser(self) -> None:
        """Show the browser view and restore mini detail if it was visible."""
        self.stacked.setCurrentWidget(self.browser)
        # Note: We don't automatically show mini detail when returning to browser
        # The user would need to click a preview again to show it

    def show_asset_detail(self, asset: dict) -> None:
        """
        Show the full detail view for the given asset.

        Args:
            asset: Asset dictionary to display
        """
        # Hide mini detail first (before switching views)
        self.hide_mini_detail()

        # Switch to detail view
        self.stacked.setCurrentWidget(self.detail)
        self.detail.draw_details(asset)

    def show_log_viewer(self, sync_result) -> None:
        """
        Show the log viewer with sync results.

        Args:
            sync_result: SyncResult object from sync operation
        """
        # Hide mini detail when showing log viewer
        self.hide_mini_detail()

        # Set the sync result and switch to log viewer
        self.log_viewer.set_sync_result(sync_result)
        self.stacked.setCurrentWidget(self.log_viewer)

    def show_mini_detail(self, asset: dict) -> None:
        """
        Show the mini detail view for the given asset.

        Args:
            asset: Asset dictionary to display
        """
        # Only show mini detail if we're in browser view, not detail view
        if self.stacked.currentWidget() != self.browser:
            return

        self.mini_detail.show_asset(asset)

        # Get current sizes
        current_sizes = self.main_splitter.sizes()

        # If mini detail is currently hidden (size is 0), show it
        if current_sizes[2] == 0:
            total = sum(current_sizes)
            # Redistribute space to show mini detail
            self.main_splitter.setSizes([
                int(total * 0.15),  # tree: 15%
                int(total * 0.65),  # browser: 65%
                int(total * 0.20)  # mini detail: 20%
            ])

    def hide_mini_detail(self) -> None:
        """Hide the mini detail view."""
        # Get current sizes
        current_sizes = self.main_splitter.sizes()

        # Only adjust if mini detail is currently visible
        if current_sizes[2] > 0:
            # Give mini detail's space to the browser/detail view
            tree_size = current_sizes[0]
            content_size = current_sizes[1] + current_sizes[2]

            self.main_splitter.setSizes([
                tree_size,  # keep tree size
                content_size,  # content area (browser or detail) gets mini detail's space
                0  # mini detail hidden
            ])

    def _on_tree_item_clicked(self, path: str) -> None:
        """Internal handler that forwards tree clicks to presenter via signal."""
        # Hide mini detail when navigating tree
        self.hide_mini_detail()
        self.treeItemSelected.emit(path)

    def _on_search_changed(self, text: str) -> None:
        """Internal handler that forwards search changes to presenter via signal."""
        # Hide mini detail when searching
        self.hide_mini_detail()
        self.searchTextChanged.emit(text)

    def _on_filter_changed(self, filter_text: str) -> None:
        """Internal handler that forwards filter changes to presenter via signal."""
        self.filterChanged.emit(filter_text)

    # UML: + showMessage(msg)
    def show_message(self, msg: str, message_type: str = "info", timeout: int = 5000) -> None:
        """
        Display a message to the user in the status bar.

        Args:
            msg: The message to display
            message_type: Type of message ('info', 'warning', 'error', 'success')
            timeout: Time in milliseconds before message clears (default: 5000ms)
        """
        self.status_bar.show_message(msg, message_type, timeout)

    # Remaining UML methods...
    def onBackClicked(self, w: QWidget) -> None:
        """Handle back navigation from a given widget."""
        pass

    def onImportClicked(self, a: Any) -> None:
        """Handle importing the given asset."""
        pass

    def onTreeItemClicked(self, i: Any) -> None:
        """Handle clicks on a tree item representing a directory or asset."""
        pass

    def onValidateDatabaseClicked(self, a: Any) -> None:
        """Trigger database validation for the given asset or scope."""
        pass

    def onEditMetadata(self, a: Any) -> None:
        """Enter an edit mode for asset metadata."""
        pass

    def onSaveMetadataChanges(self, a: Any) -> None:
        """Persist metadata changes for the given asset."""
        pass

    def _on_import_clicked(self):
        self.importClicked.emit()

    def _on_scan_clicked(self):
        self.scanClicked.emit()
