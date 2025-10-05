from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap
import os
from typing import Any, Dict, List

from frontend.Window import Window
from frontend.Preview import Preview
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
        self.previews = self._create_previews_list(self.assets)
        self.win.browser.draw_previews(self.previews)

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

    def _create_previews_list(self, assets: list) -> List[Preview]:
        """
        From a flat list of asset dicts, create a list of Preview widgets.

        Assumptions:
        - Each asset has a 'directory_path' that points to a directory containing a
          preview file named 'preview' with one of the extensions: .png, .webp, .jpg
        - The asset's display name comes from asset['name']
        - The asset id comes from asset['id'] (optional)
        """
        previews: List[Preview] = []
        if not assets:
            return previews

        for asset in assets:
            if not isinstance(asset, dict):
                continue
            name = asset.get('name', '')
            asset_id = asset.get('id')
            dir_path = asset.get('directory_path') or ''

            # Normalize the directory path
            norm = os.path.normpath(str(dir_path)) if dir_path else ''

            # Determine preview file path
            preview_path = None
            if norm:
                # Try both the normalized path and a version with a leading slash if missing
                candidate_bases = [norm]
                if not norm.startswith(os.sep):
                    candidate_bases.append(os.sep + norm)

                exts = ['.png', '.webp', '.jpg']
                for base in candidate_bases:
                    for ext in exts:
                        cand = os.path.join(base, 'preview' + ext)
                        if os.path.isfile(cand):
                            preview_path = cand
                            break
                    if preview_path:
                        break

            # Load pixmap (empty if not found)
            pixmap = QPixmap(preview_path) if preview_path else QPixmap()

            previews.append(Preview(
                thumbnail=pixmap,
                asset_name=name,
                asset_id=asset_id,
                parent=None,
            ))

        return previews


