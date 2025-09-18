import os
import sys
import requests
import pathlib

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QTreeView, QSplitter, QLabel, QMessageBox
)

BACKEND_URL = "http://127.0.0.1:8000"
ASSET_API_ENDPOINT = f"{BACKEND_URL}/assets/"
ROOT_ASSET_DIRECTORY = "Assets"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self.resize(800, 600)
        self._init_ui()
        self._reload_tree()

    def _init_ui(self):
        main_widget = QSplitter()

        # Left side: tree view of assets
        self.tree = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['File Path'])
        self.tree.setModel(self.tree_model)
        self.tree.clicked.connect(self._i_was_clicked)

        # Right side: temp
        self.label = QLabel()

        main_widget.addWidget(self.tree)
        main_widget.addWidget(self.label)
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

    def _reload_tree(self):
        """
        Builds a hierarchical QStandardItemModel displaying the directory structure
        and individual assets as leaves, based on 'directory_path' entries from assets.
        """
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(['Directory Path'])

        root_node = self.tree_model.invisibleRootItem()

        # Key: A tuple representing the full, normalized path to the directory (relative to asset root).
        # Value: The QStandardItem instance for that directory.
        path_nodes = {}

        assets = self._get_assets()

        for asset in assets:
            file_path_str = asset.get('directory_path', '')
            if not file_path_str:
                # Handle assets with no path or empty path directly under the tree's root
                item = QStandardItem(f"(No Path) {asset.get('name', 'Unnamed')}")
                item.setData(asset, Qt.ItemDataRole.UserRole)
                root_node.appendRow(item)
                continue

            path = pathlib.Path(file_path_str)
            path_components = path.parts

            # Extract the relevant path components relative to ROOT_ASSET_DIRECTORY
            display_components = []
            try:
                root_dir_index = path_components.index(ROOT_ASSET_DIRECTORY)
                display_components = list(path_components[root_dir_index + 1:])
            except ValueError:
                display_components = list(path_components)

            if not display_components:
                # Happens when asset is directly in ROOT_ASSET_DIRECTORY or the path was just a bare root
                item_text = asset.get('name', os.path.basename(file_path_str))  # Fallback to filename
                item = QStandardItem(item_text)
                item.setData(asset, Qt.ItemDataRole.UserRole)
                root_node.appendRow(item)
                continue

            # Build the nested directory structure and add the asset
            current_parent_item = root_node
            current_path_key_parts = ()  # Stores the absolute path components for dictionary key lookup

            for i, component in enumerate(display_components):
                current_path_key_parts = current_path_key_parts + (component,)

                is_last_component = (i == len(display_components) - 1)

                looks_like_file = '.' in component and is_last_component

                if is_last_component and looks_like_file:
                    item_text = component
                    asset_item = QStandardItem(item_text)
                    asset_item.setData(asset, Qt.ItemDataRole.UserRole)
                    current_parent_item.appendRow(asset_item)
                else:
                    if current_path_key_parts not in path_nodes:
                        dir_item = QStandardItem(component)
                        current_parent_item.appendRow(dir_item)
                        path_nodes[current_path_key_parts] = dir_item

                    current_parent_item = path_nodes[current_path_key_parts]

        self.tree.expandToDepth(0)

    def _i_was_clicked(self, idx: QModelIndex):
        self.label.setText(idx.data())


    @staticmethod
    def _display_message(message, title="Universal Asset Browser"):
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()



app = QApplication()
window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec()
