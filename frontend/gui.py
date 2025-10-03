from PySide6.QtWidgets import (
    QApplication
)

from MainWindow import MainWindow


app = QApplication()
window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec()
