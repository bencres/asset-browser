from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap
import os
from typing import Any, Dict, List

from frontend.window import Window
from frontend.preview import Preview
from backend.asset_service import AssetService

class Presenter(QWidget):
    def __init__(self, win: Window, asset_service: AssetService):
        super().__init__()
        self.win = win
        self.asset_service = asset_service
        self.ROOT_ASSET_DIRECTORY = "Assets"
        
        try:
            app = self._detect_application()
            self.adapter = self._set_adapter(app)
        except Exception as e:
            win.show_message(f"Error setting adapter! {e}")
            print(f"Error setting adapter! {e}")

        self.assets = self._load_assets()
        self.directory_tree = self._build_directory_tree(self.assets)

        self.previews = self._create_previews_list(self.assets)
        self.bind_events()
        self.win.browser.draw_previews(self.previews)
        self.win.tree.draw_tree(self.directory_tree)

    def run(self):
        self.win.show()

    def reload_assets(self):
        pass

    def bind_events(self):
        self.win.treeItemSelected.connect(self.on_tree_item_clicked)
        self.win.searchTextChanged.connect(self.on_search_changed)
        self.win.filterChanged.connect(self.on_filter_changed)
        self.win.scanClicked.connect(self.on_scan_clicked)
        self.win.importClicked.connect(self.on_import_clicked)
        self.win.toolbar.logViewerClicked.connect(self.on_log_viewer_clicked)

    def on_scan_clicked(self):
        sync_result = self.asset_service.sync()

        # Reload assets
        self.assets = self._load_assets()
        self.directory_tree = self._build_directory_tree(self.assets)
        self.previews = self._create_previews_list(self.assets)
        self.win.browser.draw_previews(self.previews)
        self.win.tree.draw_tree(self.directory_tree)

    def on_log_viewer_clicked(self):
        """Handle log viewer button click - show the last sync result."""
        last_result = self.asset_service.sync_service.get_last_sync_result()

        if last_result:
            self.win.show_log_viewer(last_result)
        else:
            self.win.show_message("No sync logs available. Run a scan first.")

    def on_import_clicked(self):
        self.win.show_message("Import clicked!")

    def _get_asset_by_id(self, asset_id: int) -> dict:
        # TODO: this is a quick fix. Should actually query the database.
        return next((a for a in self.assets if a.get('id') == asset_id), None)

    def on_asset_preview_clicked(self, asset_id: int) -> dict:
        asset = self._get_asset_by_id(asset_id)
        # TODO: import button and splitter are not hidden when clicking elsewhere.
        if asset:
            # Show mini detail view
            self.win.show_mini_detail(asset)

            # Show import button in toolbar
            self.win.toolbar.show_import_button()

    def on_asset_preview_double_clicked(self, asset_id: int):
        asset = self._get_asset_by_id(asset_id)
        self.win.show_asset_detail(asset)

    def on_back_clicked(self, widget: QWidget):
        pass

    def on_tree_item_clicked(self, path: str):
        """
        Handle tree item click by filtering assets for the selected directory path.
        
        Args:
            path: The directory path from the tree (e.g., "Local/HDRIs")
        """
        # Get assets that are in subdirectories of the clicked path
        filtered_assets = self._get_assets_in_directory(path)
        
        # Create previews for the filtered assets
        previews = self._create_previews_list(filtered_assets)
        
        # Update the browser display
        self.win.browser.draw_previews(previews)
        self.win.show_browser()

    def on_edit_metadata(self, asset: dict):
        pass

    def on_save_metadata_changes(self, asset: dict):
        pass

    def _set_adapter(self, app):
        pass

    def _detect_application(self):
        pass

    def _load_assets(self):
        return self.asset_service.get_assets()

    def _get_assets_in_directory(self, selected_path: str) -> List[Dict[str, Any]]:
        """
        Get all assets whose directory_path is within the selected path or any of its subdirectories.
        
        Args:
            selected_path: The path selected in the tree relative to Assets (e.g., "Local/HDRIs")
            
        Returns:
            List of asset dictionaries that are anywhere within the selected directory tree
        """
        # TODO: this is a quick fix. Should actually query the database.
        filtered_assets = []
        
        # Normalize the selected path
        selected_path_normalized = os.path.normpath(selected_path).strip('/')
        selected_parts = [p for p in selected_path_normalized.split(os.sep) if p]
        
        for asset in self.assets:
            asset_path = asset.get('directory_path', '')
            if not asset_path:
                continue
            
            # Normalize the asset path
            asset_path_normalized = os.path.normpath(asset_path).strip('/')
            asset_parts = [p for p in asset_path_normalized.split(os.sep) if p]
            
            # Find where "Assets" is in the path
            try:
                assets_index = asset_parts.index(self.ROOT_ASSET_DIRECTORY)
                # Get the path after "Assets"
                relative_parts = asset_parts[assets_index + 1:]
            except ValueError:
                # "Assets" not found in path, skip this asset
                continue
            
            # Check if asset is within the selected directory or any subdirectory
            # The asset path must be at least as long as the selected path
            # and all parts of selected_path must match the beginning of relative_parts
            if len(relative_parts) >= len(selected_parts):
                if relative_parts[:len(selected_parts)] == selected_parts:
                    filtered_assets.append(asset)
        
        return filtered_assets

    def _build_directory_tree(self, assets: list) -> Dict[str, Any]:
        """
        Build a nested dictionary representing the directory tree starting from the 'Assets' directory.
        Each path component after 'Assets' becomes a nested dict key. At the leaf directory,
        the asset is appended to a special '__assets__' list to allow UIs to access leaf items.

        Example output shape (starting from Assets):
        {
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
            parts: List[str] = [p for p in norm.split(os.sep) if p]
            
            # Find the "Assets" directory and only use the path after it
            try:
                assets_index = parts.index(self.ROOT_ASSET_DIRECTORY)
                # Get only the parts after "Assets"
                relative_parts = parts[assets_index + 1:]
            except ValueError:
                # "Assets" not found in path, skip this asset
                continue
            
            if not relative_parts:
                # Path has no components after "Assets"; attach asset at root
                leaf = tree.setdefault('__assets__', [])
                leaf.append(asset)
                continue

            node = tree
            for part in relative_parts:
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

            asset_preview = Preview(
                thumbnail=pixmap,
                asset_name=name,
                asset_id=asset_id,
                parent=None,
            )
            asset_preview.asset_clicked.connect(self.on_asset_preview_clicked)
            asset_preview.asset_double_clicked.connect(self.on_asset_preview_double_clicked)
            previews.append(asset_preview)

        return previews

    def on_search_changed(self, text: str):
        filtered_assets = self.filter_assets_by_text(text)
        self.win.browser.draw_previews(self._create_previews_list(filtered_assets))

    def on_filter_changed(self, text: str):
        print(f"Filter changed: {text}")

    def filter_assets_by_text(self, filter_text: str) -> List[Dict[str, Any]]:
        """
        Filter assets based on search text matching against name, directory path, and tags.
        
        Args:
            filter_text: The text to search for (case-insensitive)
        
        Returns:
            List of asset dictionaries that match the filter criteria
        """
        # TODO: This is a quick fix. Should actually query the database.
        if not filter_text or not filter_text.strip():
            # Return all assets if filter text is empty
            return self.assets
        
        filtered_assets = []
        search_term = filter_text.lower().strip()
        
        for asset in self.assets:
            if not isinstance(asset, dict):
                continue
            
            # Get asset properties
            asset_name = (asset.get('name') or '').lower()
            directory_path = (asset.get('directory_path') or '').lower()
            tags = asset.get('tags', [])
            
            # Check if search term matches name
            if search_term in asset_name:
                filtered_assets.append(asset)
                continue
            
            # Check if search term matches directory path
            if search_term in directory_path:
                filtered_assets.append(asset)
                continue
            
            # Check if search term matches any tag
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and search_term in tag.lower():
                        filtered_assets.append(asset)
                        break
        return filtered_assets
