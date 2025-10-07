import requests
import pathlib as pl

class SyncService:
    def __init__(self, server_url: str, asset_directory_path: str):
        self.server_url = server_url
        self.asset_directory_path = pl.Path(asset_directory_path)

    def sync(self):
        """
        1. Get list of assets from server
            - Store in a dict, key is the directory_path and value is the rest of the asset data
        2. Scan the filesystem for assets
            - Ignore the 'meta' subdirectory of the assets directory
            - For each asset candidate, store its absolute path in a set
                - For now, asset candidates are directories containing a meta.yaml file
            - Store the meta.yaml file's data in a dict, key is the filepath and value is a dict of asset data
        3. Iterate over server assets and compare to local assets
            - When a server asset is not found locally, flag it
        4. Iterate over local assets and compare to server assets
            - When a local asset is not found on the server, POST it
            - When a local asset is found on the server, update the server's version with the local version
                - Lookup the asset's meta.yaml on disk and POST it with whatever other files are there
                    - If there is no meta.yaml, create a new empty one
        5. Log the results in the `meta` subdirectory of the root directory
        """
        assets = self._get_assets()
        assets_as_k_path_to_v_meta = self._store_assets_by_path(assets)


    def _get_assets(self):
        """Get assets from the server."""
        # TODO: The same method is implemented in `asset_service.py`. Consider refactoring.
        try:
            response = requests.get(self.server_url + "/assets")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)

    def _store_assets_by_path(self, assets: dict) -> dict:
        """Stores assets by their directory path in a dict.

        Args:
            assets (dict): Dictionary of assets from the server

        Returns:
            dict: Dictionary with directory paths as keys and asset data as values
        """
        assets_by_path = {}
        if not assets:
            return assets_by_path

        for asset in assets:
            if 'directory_path' in asset:
                key = asset['directory_path']
                value = asset
                del value['directory_path']
                assets_by_path[key] = value

        return assets_by_path

    def _get_local_asset_dir_paths(self, asset_directory_path: str) -> set:
        """Get asset directory paths from the local filesystem.
        
        Args:
            asset_directory_path (str): Path to the asset directory
            
        Returns:
            set: Set of absolute paths to directories containing meta.yaml files
        """
        asset_paths = set()
        p = pl.Path(asset_directory_path)

        if not p.exists():
            return asset_paths

        for p in p.rglob("*"):
            if p.is_dir() and p.name != 'meta': # Ignore the 'meta' subdirectory
                meta_file = p / 'meta.yaml'
                if meta_file.exists():
                    asset_paths.add(str(p.absolute()))

        return asset_paths

    def _get_meta_files_from_dirs(self, assets):
        """Get the meta file from each asset's directory."""
        pass

    def _compare_local_paths_to_server_paths(self, local_asset_dir_paths: set, server_assets: list):
        """Compare local asset paths to server asset paths."""
        for a in server_assets:
            if a["directory_path"] in local_asset_dir_paths:
                continue
            else:
                self._handle_missing_asset_in_local(a)

        server_asset_dir_paths = set([a["directory_path"] for a in server_assets])

        for la in local_asset_dir_paths:
            if la not in server_asset_dir_paths:
                self._handle_missing_asset_in_server(self._create_local_asset_from_path(la))

    def _handle_missing_asset_in_server(self, asset_request_body):
        """Handle missing asset in server."""
        # POST the missing asset

        try:
            requests.post(self.server_url, asset_request_body)
        except Exception as e:
            print(e)

    def _handle_missing_asset_in_local(self, asset):
        """Handle missing asset in local."""
        # Warn the user

    def _create_local_asset_from_path(self, asset_path: str) -> dict:
        """Get the local asset from the given path."""
        """name: str
        description: Optional[str] = None
        directory_path: str"""
        directory_path = asset_path
        asset_path = pl.Path(asset_path)
        # TODO: get asset data from meta file.
        # meta_file = asset_path / 'meta.yaml'
        name = asset_path.name
        description = None
        body = {
            "name": name,
            "description": description,
            "directory_path": directory_path
        }
        return body


    def _parse_meta_file(self, meta_file_path: str):
        """Parse the meta file."""
        pass



