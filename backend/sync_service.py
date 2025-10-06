class SyncService:
    def __init__(self):
        pass

    def sync(self):
        """
        1. Get list of assets from server
            - Store by path
        2. Scan the filesystem for assets
            - Store in a set
            - Store the meta.yaml for each asset by path on disk
        3. Iterate over server assets and compare to local assets
            - When a server asset is not found locally, flag it
        4. Iterate over local assets and compare to server assets
            - When a local asset is not found on the server, POST it
            - When a local asset is found on the server, update the server's version with the local version
                - Lookup the asset's meta.yaml on disk and POST it with whatever other files are there
                    - If there is no meta.yaml, create a new empty one
        5. Log the results in the `meta` subdirectory of the root directory

        """

        pass