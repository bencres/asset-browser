import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QTreeView, QSplitter, QLabel
)
import requests

BACKEND_URL = "http://127.0.0.1:8000"
ASSET_API_ENDPOINT = f"{BACKEND_URL}/assets/"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self._init_ui()

    def _init_ui(self):
        main_widget = QSplitter()
        self.tree = QTreeView()
        self.label = QLabel()
        main_widget.addWidget(self.tree)
        main_widget.addWidget(self.label)
        self.setCentralWidget(main_widget)

app = QApplication()
window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec()
