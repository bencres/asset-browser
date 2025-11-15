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
        self.assets = []
        self.previews = []
        self.current_asset = None

        self.widget = view
        self.win = None

        # TODO: this is just placeholder
        self.widget.toolbar.set_allowed_renderers(
            ["Karma", "Mantra", "Renderman", "Redshift", "Arnold", "V-Ray"])

        self.bind_events()
        self._refresh_gui()

    def bind_events(self):
        self.widget.search_text_changed.connect(self.on_search_changed)
        self.widget.filter_changed.connect(self.on_filter_changed)
        self.widget.scan_clicked.connect(self.on_scan_clicked)
        self.widget.import_clicked.connect(self.on_import_asset)
        self.widget.renderer_changed.connect(self.on_renderer_changed)
        self.widget.delete_asset_clicked.connect(self.on_delete_asset)

    def spawn_asset(self, asset: dict):
        # Implemented in derived classes
        pass

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
        if not asset_path:
            print("Importing asset: MISSING PATH")
            return

        if os.path.isdir(asset_path):
            print(f"Importing assets from directory: {asset_path}")
            imported_count = 0
            skipped_count = 0
            print(os.listdir(asset_path))
            for filename in os.listdir(asset_path):
                file_path = os.path.join(asset_path, filename)
                # TODO: add support for other file types
                if os.path.isfile(file_path) and filename.lower().endswith('.hdr'):
                    asset = self.asset_service.create_asset_req_body_from_path(
                        file_path)
                    self.asset_service.add_asset_to_db(asset)
                    imported_count += 1
                else:
                    skipped_count += 1
            self._refresh_gui()
            self.widget.show_message(
                f"Imported {imported_count} .hdr asset(s) from directory. Skipped {skipped_count} non-hdr file(s).", "info", 3000)
        else:
            print(f"Importing asset: {asset_path}")
            asset = self.asset_service.create_asset_req_body_from_path(
                asset_path)
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

    def on_asset_mini_detail_clicked(self, asset_id: int) -> None:
        asset = self.asset_service.get_asset_by_id(asset_id)
        self.widget.toggle_mini_detail(asset)

    def on_asset_preview_clicked(self, asset_id: int) -> None:
        preview = self.get_preview_by_id(asset_id)
        self.current_asset = self.asset_service.get_asset_by_id(asset_id)
        self.widget.set_new_selected_preview(preview)
        self.widget.show_message(
            f"Asset clicked: {self.current_asset['name']}", "info", 3000)

    def get_preview_by_id(self, id: int) -> Preview:
        return next((p for p in self.previews if p.asset_id == id), None)

    def on_asset_preview_double_clicked(self, asset_id: int):
        asset = self.asset_service.get_asset_by_id(asset_id)
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
        self.widget.draw_previews(self.previews)

    def _load_assets(self):
        return self.asset_service.get_assets()

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
            asset_preview = Preview(
                asset_id,
                thumbnail=pixmap,
                asset_name=name,
                parent=None,
            )
            # Connect events
            asset_preview.show_mini_details.connect(
                self.on_asset_mini_detail_clicked)
            asset_preview.asset_double_clicked.connect(
                self.on_asset_preview_double_clicked)
            asset_preview.asset_clicked.connect(
                self.on_asset_preview_clicked)
            previews.append(asset_preview)

        return previews

    def on_search_changed(self, text: str, delay: int = 200) -> None:
        if not hasattr(self, "_search_debounce_timer"):
            from PySide6.QtCore import QTimer
            self._search_debounce_timer = QTimer(self)
            self._search_debounce_timer.setSingleShot(True)
            self._search_debounce_timer.timeout.connect(self._trigger_search)

        self._pending_search_text = text
        self._search_debounce_timer.start(delay)

    def _trigger_search(self):
        text = getattr(self, "_pending_search_text", "")
        filtered_assets = self.asset_service.search_assets(text)
        self.widget.draw_previews(
            self._create_previews_list(filtered_assets))
        self.widget.show_browser()

    def on_filter_changed(self, text: str):
        print(f"Filter changed: {text}")
