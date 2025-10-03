from PySide6.QtWidgets import (
    QApplication
)

from frontend.MainWindow import MainWindow

BACKEND_URL = "http://127.0.0.1:8000"
ASSET_API_ENDPOINT = f"{BACKEND_URL}/assets/"
ROOT_ASSET_DIRECTORY = "Assets"

app = QApplication()
window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec()
