from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap
import os
from typing import Any, Dict, List

from uab.frontend.preview import Preview
from uab.backend.asset_service import AssetService
from uab.core import utils


class Presenter(QWidget):
    def __init__(self, view):
        super().__init__()
        LOCAL_ASSETS_DIR = "/Users/dev/Assets"
        SERVER_URL = "http://127.0.0.1:8000"
        self.asset_service = AssetService(SERVER_URL, LOCAL_ASSETS_DIR)
        self.ROOT_ASSET_DIRECTORY = "Assets"
        self.widget = view
        self.win = None

        # TODO: this is just placeholder
        self.widget.toolbar.set_allowed_renderers(
            ["Karma", "Mantra", "Renderman", "Redshift", "Arnold", "V-Ray"])

        self.assets = self._load_assets()

        self.previews = self._create_previews_list(self.assets)
        self.bind_events()
        self.widget.browser.draw_previews(self.previews)

    def reload_assets(self):
        pass

    def bind_events(self):
        self.widget.search_text_changed.connect(self.on_search_changed)
        self.widget.filter_changed.connect(self.on_filter_changed)
        self.widget.scan_clicked.connect(self.on_scan_clicked)
        self.widget.import_clicked.connect(self.on_import_asset)
        self.widget.renderer_changed.connect(self.on_renderer_changed)
        self.widget.delete_asset_clicked.connect(self.on_delete_asset)

    def on_scan_clicked(self):
        self.widget.show_message("Starting sync operation...", "info")

        sync_result = self.asset_service.sync()

        self._refresh_gui()
        self.widget.show_browser()

        # Show completion message in status bar
        summary = sync_result.get_summary()
        if summary['error_count'] > 0:
            self.widget.show_message(
                f"Sync completed with {summary['error_count']} errors",
                "warning",
                10000
            )
        else:
            self.widget.show_message(
                f"Sync completed successfully - {summary['assets_posted']} assets posted",
                "success",
                5000
            )

    def on_import_asset(self, asset_path):
        print(
            f"Importing asset: {asset_path if asset_path else 'MISSING PATH'}")
        asset = self.asset_service.create_asset_req_body_from_path(asset_path)
        self.asset_service.add_asset_to_db(asset)
        self._refresh_gui()
        self.widget.show_message(
            f"Imported asset! {asset['name']}", "info", 3000)

    def on_delete_asset(self, asset_id):
        self.asset_service.remove_asset_from_db(asset_id)
        self._refresh_gui()
        self.widget.show_browser()
        self.widget.show_message(f"Deleted asset!", "info", 3000)

    def on_renderer_changed(self, renderer_text: str):
        self.widget.show_message(
            f"Renderer changed to {renderer_text}", "info", 3000)

    def on_log_viewer_clicked(self):
        """Show log viewer with most recent sync results."""
        last_result = self.asset_service.sync_service.get_last_sync_result()

        if last_result:
            self.widget.show_log_viewer(last_result)
        else:
            self.widget.show_message(
                "No sync logs available. Run a scan first.", "warning", 3000)

    def _get_asset_by_id(self, asset_id: int) -> dict:
        # TODO: this is a quick fix. Should actually query the database.
        return next((a for a in self.assets if a.get('id') == asset_id), None)

    def on_asset_preview_clicked(self, asset_id: int) -> None:
        asset = self._get_asset_by_id(asset_id)
        if not asset:
            self.widget.show_message("Asset not found!", "warning", 3000)
            return

        self.widget.toggle_mini_detail(asset)

    def on_asset_preview_double_clicked(self, asset_id: int):
        asset = self._get_asset_by_id(asset_id)
        self.widget.show_asset_detail(asset)

    def on_back_clicked(self, widget: QWidget):
        pass

    def on_edit_metadata(self, asset: dict):
        pass

    def on_save_metadata_changes(self, asset: dict):
        pass

    def _refresh_gui(self):
        self.assets = self._load_assets()
        self.previews = self._create_previews_list(self.assets)
        self.widget.browser.draw_previews(self.previews)

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
        selected_parts = [
            p for p in selected_path_normalized.split(os.sep) if p]

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


    def _create_previews_list(self, assets: list) -> List[Preview]:
        """
        From a flat list of asset dicts, create a list of Preview widgets.

        Assumptions:
        - Each asset has a 'directory_path' that either:
          1. Points to a directory containing a preview file named 'preview' with 
             one of the extensions: .png, .webp, .jpg, OR
          2. Points directly to a .hdr file that will be tone-mapped to create a preview
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

            pixmap = QPixmap()

            # Check if directory_path is a .hdr file
            if norm and norm.lower().endswith('.hdr') and os.path.isfile(norm):
                try:
                    # Use hdr_to_preview to generate a tone-mapped preview
                    byte_image = utils.hdr_to_preview(norm, as_bytes=True)
                    # Convert PIL Image to QPixmap
                    # First convert to bytes, then load into QPixmap
                    pixmap.loadFromData(byte_image)
                except Exception as e:
                    print(f"Error loading HDR preview for {norm}: {e}")
                    pixmap = QPixmap()
            else:
                # Original behavior: look for preview file in directory
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
            asset_preview.show_mini_details.connect(
                self.on_asset_preview_clicked)
            asset_preview.asset_double_clicked.connect(
                self.on_asset_preview_double_clicked)
            previews.append(asset_preview)

        return previews

    def on_search_changed(self, text: str):
        filtered_assets = self.filter_assets_by_text(text)
        self.widget.browser.draw_previews(
            self._create_previews_list(filtered_assets))
        self.widget.show_browser()

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
