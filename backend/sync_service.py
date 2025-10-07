import requests
import pathlib as pl
from datetime import datetime
from typing import Dict, List, Set, Any
from enum import Enum


class SyncLogLevel(Enum):
    """Log levels for sync operations."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class SyncLogEntry:
    """Represents a single log entry from a sync operation."""
    
    def __init__(self, level: SyncLogLevel, message: str, asset_path: str = None):
        self.timestamp = datetime.now()
        self.level = level
        self.message = message
        self.asset_path = asset_path
    
    def __str__(self):
        time_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        asset_info = f" [{self.asset_path}]" if self.asset_path else ""
        return f"[{time_str}] [{self.level.value}]{asset_info} {self.message}"
    
    def to_dict(self):
        """Convert log entry to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'asset_path': self.asset_path
        }


class SyncResult:
    """Contains the results of a sync operation."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.server_asset_count = 0
        self.local_asset_count = 0
        self.assets_posted = []
        self.assets_missing_locally = []
        self.errors = []
        self.log_entries: List[SyncLogEntry] = []
    
    def complete(self):
        """Mark the sync operation as complete."""
        self.end_time = datetime.now()
    
    @property
    def duration(self):
        """Get the duration of the sync operation."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def add_log(self, level: SyncLogLevel, message: str, asset_path: str = None):
        """Add a log entry."""
        entry = SyncLogEntry(level, message, asset_path)
        self.log_entries.append(entry)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the sync results."""
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'server_asset_count': self.server_asset_count,
            'local_asset_count': self.local_asset_count,
            'assets_posted': len(self.assets_posted),
            'assets_missing_locally': len(self.assets_missing_locally),
            'error_count': len(self.errors),
            'log_entry_count': len(self.log_entries)
        }
    
    def get_logs_by_level(self, level: SyncLogLevel) -> List[SyncLogEntry]:
        """Get all log entries of a specific level."""
        return [entry for entry in self.log_entries if entry.level == level]



class SyncService:
    def __init__(self, server_url: str, asset_directory_path: str):
        self.server_url = server_url
        self.local_asset_directory_path = pl.Path(asset_directory_path)
        self.last_sync_result: SyncResult = None

    def sync(self) -> SyncResult:
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
        result = SyncResult()
        self.last_sync_result = result
        
        result.add_log(SyncLogLevel.INFO, "Starting sync operation")
        
        # Step 1: Get server assets
        server_assets = self._get_assets(result)
        result.server_asset_count = len(server_assets) if server_assets else 0
        
        # Step 2: Scan local filesystem
        server_assets_as_k_path_to_v_data = self._store_assets_by_path(server_assets)
        local_asset_dir_paths = self._get_local_asset_dir_paths(str(self.local_asset_directory_path), result)
        result.local_asset_count = len(local_asset_dir_paths)
        
        # Step 3 & 4: Sync assets
        self._sync_local_assets_with_server_assets(local_asset_dir_paths, server_assets, result)
        
        result.complete()
        result.add_log(SyncLogLevel.INFO, f"Sync completed in {result.duration:.2f} seconds")
        
        return result

    def update_configuration(self, server_url: str = None, asset_directory_path: str = None):
        """Update service configuration without losing sync history."""
        if server_url:
            self.server_url = server_url
        if asset_directory_path:
            self.local_asset_directory_path = pl.Path(asset_directory_path)

    def get_last_sync_result(self) -> SyncResult:
        """Get the result of the last sync operation."""
        return self.last_sync_result

    def _get_assets(self, result: SyncResult):
        """Get assets from the server."""
        # TODO: The same method is implemented in `asset_service.py`. Consider refactoring.
        try:
            result.add_log(SyncLogLevel.INFO, f"Fetching assets from server: {self.server_url}")
            response = requests.get(self.server_url + "/assets")
            response.raise_for_status()
            assets = response.json()
            result.add_log(SyncLogLevel.SUCCESS, f"Retrieved {len(assets)} assets from server")
            return assets
        except Exception as e:
            result.add_log(SyncLogLevel.ERROR, f"Failed to get assets from server: {e}")
            result.errors.append(str(e))
            print(e)
            return []

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
                assets_by_path[asset['directory_path']] = asset

        return assets_by_path

    def _get_local_asset_dir_paths(self, asset_directory_path: str, result: SyncResult) -> set:
        """Get asset directory paths from the local filesystem.
        
        Args:
            asset_directory_path (str): Path to the asset directory
            result (SyncResult): Result object to log to
            
        Returns:
            set: Set of absolute paths to directories containing meta.yaml files
        """
        asset_paths = set()
        p = pl.Path(asset_directory_path)

        if not p.exists():
            result.add_log(SyncLogLevel.ERROR, f"Asset directory does not exist: {asset_directory_path}")
            return asset_paths

        result.add_log(SyncLogLevel.INFO, f"Scanning local filesystem: {asset_directory_path}")
        
        for p in p.rglob("*"):
            if p.is_dir() and p.name != 'meta': # Ignore the 'meta' subdirectory
                meta_file = p / 'meta.yaml'
                if meta_file.exists():
                    asset_paths.add(str(p.absolute()))

        result.add_log(SyncLogLevel.SUCCESS, f"Found {len(asset_paths)} local assets")
        return asset_paths

    def _get_meta_files_from_dirs(self, assets):
        """Get the meta file from each asset's directory."""
        pass

    def _sync_local_assets_with_server_assets(self, local_asset_dir_paths: set, server_assets: list, result: SyncResult):
        """Compare local asset paths to server asset paths."""
        # TODO: normalize paths.
        for a in server_assets:
            if not a["directory_path"].startswith("/"):
                a["directory_path"] = "/" + a["directory_path"]
        
        # Check for server assets missing locally
        for a in server_assets:
            if a["directory_path"] in local_asset_dir_paths:
                continue
            else:
                self._handle_missing_asset_in_local(a, result)

        server_asset_dir_paths = set([a["directory_path"] for a in server_assets])

        # Check for local assets missing on server
        for la in local_asset_dir_paths:
            if la not in server_asset_dir_paths:
                self._handle_missing_asset_in_server(self._create_local_asset_from_path(la), result)

    def _handle_missing_asset_in_server(self, asset_request_body, result: SyncResult):
        """Handle missing asset in server."""
        # POST the missing asset
        asset_name = asset_request_body.get('name', 'unknown')
        asset_path = asset_request_body.get('directory_path', '')
        
        try:
            result.add_log(SyncLogLevel.INFO, f"Posting new asset to server: {asset_name}", asset_path)
            response = requests.post(self.server_url + "/assets", json=asset_request_body)
            response.raise_for_status()  # Raise an exception for bad status codes
            result.add_log(SyncLogLevel.SUCCESS, f"Successfully posted asset: {asset_name}", asset_path)
            result.assets_posted.append(asset_request_body)
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to post asset '{asset_name}': {e}"
            result.add_log(SyncLogLevel.ERROR, error_msg, asset_path)
            result.errors.append(error_msg)
            print(f"Error posting asset: {e}")

    def _handle_missing_asset_in_local(self, asset, result: SyncResult):
        """Handle missing asset in local."""
        asset_name = asset.get('name', 'unknown')
        asset_path = asset.get('directory_path', '')
        
        result.add_log(SyncLogLevel.WARNING, f"Server asset not found locally: {asset_name}", asset_path)
        result.assets_missing_locally.append(asset)

    def _create_local_asset_from_path(self, asset_path: str) -> dict:
        """Create a local asset from a directory path."""
        return {
            'name': pl.Path(asset_path).name,
            'directory_path': asset_path
        }

