from PySide6.QtWidgets import QWidget

import os
from typing import Any, Dict, List

from frontend.Window import Window
from backend.DataController import DataController

class Presenter(QWidget):
    def __init__(self, win: Window, dc: DataController):
        super().__init__()
        self.win = win
        self.dc = dc
        try:
            app = self._detect_application()
            self.adapter = self._set_adapter(app)
        except Exception as e:
            win.show_message(f"Error setting adapter! {e}")
        self.assets = self._load_assets()
        print(self.assets)
        self.tree = self._build_directory_tree(self.assets)
        print(self.tree)

    def run(self):
        self.win.show()

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

    def _set_adapter(self, app):
        pass

    def _detect_application(self):
        pass

    def _load_assets(self):
        return self.dc.get_assets()

    def _build_directory_tree(self, assets: list) -> Dict[str, Any]:
        """
        Build a nested dictionary representing the directory tree implied by each asset's
        'directory_path'. Each path component becomes a nested dict key. At the leaf directory,
        the asset is appended to a special '__assets__' list to allow UIs to access leaf items.

        Example output shape (abridged):
        {
            'Users': {
                'dev': {
                    'Assets': {
                        'Local': {
                            'HDRIs': {
                                'Outdoors': {
                                    'Dawn': {
                                        'dawn_farm_01': {
                                            '__assets__': [asset_obj]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        tree: Dict[str, Any] = {}
        if not assets:
            return tree

        for asset in assets:
            path_str = (asset or {}).get('directory_path')
            if not path_str or not isinstance(path_str, str):
                # Skip assets without a valid directory path
                continue

            # Normalize separators and strip leading/trailing slashes to avoid empty components
            norm = os.path.normpath(path_str).strip('/')
            parts: List[str] = [p for p in norm.split('/') if p]
            if not parts:
                # Path collapsed to nothing; attach asset at root
                leaf = tree.setdefault('__assets__', [])
                leaf.append(asset)
                continue

            node = tree
            for part in parts:
                node = node.setdefault(part, {})

            # Attach the asset to the leaf directory
            leaf_assets = node.setdefault('__assets__', [])
            leaf_assets.append(asset)

        return tree

    def _build_preview_list(self, dir: str):
        pass


