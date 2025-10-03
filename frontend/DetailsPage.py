from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class DetailsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.label = QLabel("No asset selected")
        layout.addWidget(self.label)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

    def set_asset(self, asset: dict):
        self.label.setText(f"Asset Details:\n{asset}")

    def go_back(self):
        print("Clicked the back button.")