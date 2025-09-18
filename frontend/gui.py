import sys
import requests
import pathlib

from PySide6.QtCore import QModelIndex
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
        root_node = self.tree_model.invisibleRootItem()
        dirs = {}
        assets = self._get_assets()
        for asset in assets:
            path = pathlib.PosixPath(asset["directory_path"])
            path_parts = list(path.parts)
            path_from_root = []
            is_dir_after_root = False
            # get the path on disc from the asset root dir
            for subdir in path_parts:
                if is_dir_after_root:
                    path_from_root.append(subdir)
                    continue
                if subdir == ROOT_ASSET_DIRECTORY:
                    is_dir_after_root = True
            # add new directories to the dirs dictionary to create the tree
            for subdir in path_from_root:
                if subdir in dirs:
                    continue
                dirs[subdir] = None
        for dir in dirs:
            item = QStandardItem(dir)
            root_node.appendRow(item)

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
