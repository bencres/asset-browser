import pathlib as pl
import requests

class AssetService:
    def __init__(self, server_url: str, asset_directory_path: str):
        self.url = server_url
        self.asset_directory_path = pl.Path(asset_directory_path)

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

    def add_asset_to_db(self, asset_request_body: dict):
        asset_name = asset_request_body.get('name', 'unknown')
        asset_path = asset_request_body.get('directory_path', '')
        try:
            response = requests.post(self.url + "/assets", json=asset_request_body)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error posting asset {asset_name} at {asset_path}: {e}")

    def remove_asset_from_db(self, asset_id: int):
        try:
            response = requests.delete(self.url + f"/assets/{asset_id}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error deleting asset with id {asset_id}: {e}")

    @staticmethod
    def create_asset_req_body_from_path(asset_path: str):
        return {
            'name': pl.Path(asset_path).name,
            'directory_path': asset_path
        }
