from PySide6.QtWidgets import QMainWindow

from uab.frontend.main_widget import MainWidget

class MainWindow(QMainWindow):
    """
    Thin QMainWindow wrapper that hosts the MainWidget as its central widget.
    """

    def __init__(self, main_widget: MainWidget) -> None:
        super().__init__()
        self.setWindowTitle("Universal Asset Browser")
        self.resize(1050, 700)

        # Central widget is now a clean, self-contained MainWidget
        self.main_widget = main_widget
        self.setCentralWidget(self.main_widget)
