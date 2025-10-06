import requests
class SyncService:
    def __init__(self):
        pass

    def sync(self, server_url: str, asset_directory_path: str):
        """
        1. Get list of assets from server
            - Store in a dict, key is the directory_path and value is the rest of the asset data
        2. Scan the filesystem for assets
            - Ignore the 'meta' subdirectory of the assets directory
            - For each asset candidate, store its absolute path in a set
                - For now, asset candidates are directories containing a meta.yaml file
            - Store the meta.yaml file's data in a dict, key is the filepath and value is a dict of asset data
                - If meta.yaml is empty,
        3. Iterate over server assets and compare to local assets
            - When a server asset is not found locally, flag it
        4. Iterate over local assets and compare to server assets
            - When a local asset is not found on the server, POST it
            - When a local asset is found on the server, update the server's version with the local version
                - Lookup the asset's meta.yaml on disk and POST it with whatever other files are there
                    - If there is no meta.yaml, create a new empty one
        5. Log the results in the `meta` subdirectory of the root directory
        """
        assets = self.get_assets(server_url + '/assets')
        assets_as_k_path_to_v_meta = self.store_assets_by_path(assets)



        pass

    def get_assets(self, url):
        """Get assets from the server."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)

    def store_assets_by_path(self, assets: dict) -> dict:
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
