import sys

from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QTreeView, QSplitter, QLabel, QMessageBox
)
import requests

BACKEND_URL = "http://127.0.0.1:8000"
ASSET_API_ENDPOINT = f"{BACKEND_URL}/assets/"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self._init_ui()
        self._get_assets()
        self._reload_tree()

    def _init_ui(self):
        main_widget = QSplitter()

        # Left side: tree view of assets
        self.tree = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['File Path'])
        self.tree.setModel(self.tree_model)

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
        pass

    def _display_message(self, message, title="Universal Asset Browser"):
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()



app = QApplication()
window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec()
