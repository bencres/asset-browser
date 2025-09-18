import os
import sys
import requests
import pathlib

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QTreeView, QSplitter, QLabel, QMessageBox, QWidget, QGridLayout,
    QVBoxLayout, QSizePolicy, QScrollArea
)

BACKEND_URL = "http://127.0.0.1:8000"
ASSET_API_ENDPOINT = f"{BACKEND_URL}/assets/"
ROOT_ASSET_DIRECTORY = "Assets"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self.resize(800, 600)
        self.assets = self._get_assets()
        self._init_ui()
        self._reload_tree(self.assets)

    def _init_ui(self):
        main_widget = QSplitter()

        # Left side: tree view of assets
        self.tree = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['File Path'])
        self.tree.setModel(self.tree_model)
        self.tree.clicked.connect(self.on_tree_item_selected)

        # Right side: grid of assets
        self.grid = IconGrid()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.grid)

        main_widget.addWidget(self.tree)
        main_widget.addWidget(self.grid)
        self.setCentralWidget(main_widget)

    def _get_assets(self):
        try:
            response = requests.get(ASSET_API_ENDPOINT)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError:
            self._display_message("Could not connect to the backend.", "Connection Error")
        except requests.exceptions.RequestException as e:
            self._display_message(f"Error loading assets: {e}", "API Error")

    def _reload_tree(self, assets):
        """
        Builds a hierarchical QStandardItemModel displaying the directory structure
        and individual assets as leaves, based on 'file_path' entries from assets.
        Stores asset data (dict) for file nodes and full path (str) for directory nodes
        in Qt.UserRole.
        """
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['File Path'])

        root_node = self.tree_model.invisibleRootItem()

        # path_nodes dictionary:
        # Key: A tuple representing the full, absolute path of a directory (e.g., ('/', 'Users', 'Me', 'project', 'my_assets'))
        # Value: The QStandardItem instance corresponding to that directory in the tree.
        path_nodes = {}

        assets.sort(key=lambda a: a.get('directory_path', ''))  # Sort for consistent tree building

        for asset in assets:
            file_path_str = asset.get('directory_path', '')
            if not file_path_str:
                item = QStandardItem(f"(No Path) {asset.get('name', 'Unnamed')}")
                item.setData(asset, Qt.ItemDataRole.UserRole)  # Store the full asset dict
                root_node.appendRow(item)
                continue

            path = pathlib.Path(file_path_str)
            path_components = path.parts

            display_components = []
            full_path_for_key_prefix = ()  # Path components for the part leading up to/including ROOT_ASSET_DIRECTORY

            try:
                root_dir_index = path_components.index(ROOT_ASSET_DIRECTORY)
                full_path_for_key_prefix = path_components[
                    :root_dir_index + 1]
                display_components = list(
                    path_components[root_dir_index + 1:])
            except ValueError:
                # If ROOT_ASSET_DIRECTORY is not found, treat the whole path as relevant.
                full_path_for_key_prefix = path_components
                display_components = list(path_components)

            if not display_components:
                item_text = asset.get('name', os.path.basename(file_path_str))
                item = QStandardItem(item_text)
                item.setData(asset, Qt.ItemDataRole.UserRole)
                root_node.appendRow(item)
                continue

            current_parent_item = root_node
            # This tuple will build up the full absolute path of the current directory/file component being processed.
            # It's used as the key for path_nodes and the data for directory items.
            current_absolute_path_key_tuple = full_path_for_key_prefix

            for i, component in enumerate(display_components):
                current_absolute_path_key_tuple = current_absolute_path_key_tuple + (component,)

                if current_absolute_path_key_tuple not in path_nodes:
                    dir_item = QStandardItem(component)
                    dir_path_string = str(pathlib.Path(*current_absolute_path_key_tuple))
                    dir_item.setData(dir_path_string, Qt.ItemDataRole.UserRole)

                    current_parent_item.appendRow(dir_item)
                    path_nodes[current_absolute_path_key_tuple] = dir_item

                current_parent_item = path_nodes[current_absolute_path_key_tuple]

        self.tree.expandToDepth(0)


    def on_tree_item_selected(self, idx: QModelIndex):
        dir_path = idx.data(Qt.ItemDataRole.UserRole)
        self._populate_icon_grid_from_directory(str(dir_path))

    def _populate_icon_grid_from_directory(self, directory_path: str):
        """
        Scans a given directory and its immediate subdirectories for 'preview' images.
        Populates the IconGrid with FileIconWidgets for each subdirectory that contains a preview.
        """
        # WARNING: paths in db currently do not have the first slash, making them all not valid paths
        # TODO: FIX THIS.
        directory_path = "/" + directory_path
        self.grid.clear()  # Clear any existing icons

        found_previews = []  # List to store (QPixmap, subdirectory_name) tuples

        # Check if the provided path actually exists and is a directory
        if not os.path.isdir(directory_path):
            self._display_message(f"Directory not found: {directory_path}", "Error")
            return

        # Traverse the immediate subdirectories of the given directory_path
        for root, dirs, files in os.walk(directory_path):
            # Only process the immediate subdirectories of the starting path for this iteration
            if root != directory_path and not root.startswith(directory_path + os.sep):
                # This breaks if we want to scan deeper than just immediate children
                # For "immediate subdirectories" as requested, we process one level deep
                continue

            # Check files in the current directory (or its subdirs if we walked deeper)
            for d in dirs:  # Iterate through each subdirectory within the current `root`
                subdir_full_path = os.path.join(root, d)
                preview_image_path = None

                # Look for a preview file directly inside this subdirectory
                for ext in ['.jpg', '.webp', '.png', '.jpeg']:  # Common image extensions
                    potential_preview = os.path.join(subdir_full_path, 'preview' + ext)
                    if os.path.isfile(potential_preview):
                        preview_image_path = potential_preview
                        break  # Found a preview, move to the next subdirectory

                if preview_image_path:
                    # Found a preview, create a QPixmap
                    pixmap = QPixmap(preview_image_path)
                    if not pixmap.isNull():
                        found_previews.append((pixmap, d))  # d is the subdirectory name
                    else:
                        # Handle cases where the image file exists but is corrupted/invalid
                        print(f"Warning: Could not load preview image for {subdir_full_path}: {preview_image_path}")
                        # You might append a placeholder pixmap here if desired
                        found_previews.append((QPixmap(), d))  # Empty pixmap will trigger placeholder in FileIconWidget
                # else: No preview found for this subdirectory, skip it

        self.grid.add_file_widgets(found_previews)
        if not found_previews:
            self._display_message(f"No previews found in '{directory_path}' or its subdirectories.", "No Previews")



    @staticmethod
    def _display_message(message, title="Universal Asset Browser"):
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()



class FileIconWidget(QWidget):
    def __init__(self, pixmap: QPixmap, text: str):
        super().__init__()
        if len(text) > 10:
            text = text[:7] + "..."
        else:
            text = text[:10]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

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


class IconGrid(QWidget):

    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setSpacing(2)
        self.grid.setContentsMargins(2, 2, 2, 2)

    def clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

    def add_file_widgets(self, files):
        """files is a list of (QPixmap, filename)"""
        self.clear()
        cols = 8
        row, col = 0, 0
        for pixmap, name in files:
            widget = FileIconWidget(pixmap, name)
            widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.grid.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1


app = QApplication()
window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec()
