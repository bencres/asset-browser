from PySide6.QtWidgets import QWidget

from frontend.MainWindow import MainWindow
from backend.DataController import DataController

class Presenter:
    def __init__(self, win: MainWindow, dc: DataController):
        self.win = win
        self.dc = dc
        app = self._detect_application()
        self.adapter = self.setAdapter(app)

    def run(self):
        self.win.show()

    def set_adapter(self, app):
        pass

    def on_asset_preview_clicked(self, asset: dict):
        pass

    def on_asset_preview_double_clicked(self, asset: dict):
        pass

    def on_back_clicked(self, widget: QWidget):
        pass

    def on_import_clicked(self, asset: dict):
        pass

    def on_tree_item_clicked(self, item_idx: int):
        pass

    def on_validate_database_clicked(self, asset: dict):
        pass

    def on_edit_metadata(self, asset: dict):
        pass

    def on_save_metadata_changes(self, asset: dict):
        pass

    def _detect_application(self):
        pass

    def _load_assets(self):
        pass

    def _build_directory_tree(self, assets: list):
        pass


