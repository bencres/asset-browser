from PySide6.QtWidgets import QWidget, QGridLayout, QSizePolicy

from FileIconWidget import FileIconWidget


class IconGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setSpacing(1)
        self.grid.setContentsMargins(1, 1, 1, 1)

    def clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
            elif item.layout():
                pass

    def add_file_widgets(self, files):
        self.clear()
        cols = 8
        row, col = 0, 0
        for pixmap, name, asset in files:
            widget = FileIconWidget(pixmap, name, asset)
            widget.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            self.grid.addWidget(widget, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1

        if col < cols:
            self.grid.setColumnStretch(col, 1)

        self.grid.setRowStretch(row, 1)
