import pathlib as pl
import requests

from backend.sync_service import SyncService, SyncResult


class AssetService:
    def __init__(self, server_url: str, asset_directory_path: str):
        self.url = server_url
        self.asset_directory_path = pl.Path(asset_directory_path)
        self.sync_service = SyncService(server_url, asset_directory_path)

    def get_assets(self):
        try:
            response = requests.get(self.url + "/assets")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)

    def set_asset_directory(self, directory_path: str):
        """Update the asset directory and recreate the sync service."""
        self.asset_directory_path = pl.Path(directory_path)
        self.sync_service.update_configuration(asset_directory_path=directory_path)

    def sync(self) -> SyncResult:
        return self.sync_service.sync()
