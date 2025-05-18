"""
File scanner module for AssetHub.

This module provides functionality to scan directories for 3D assets and catalog them.
"""
import os
import mimetypes
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
import logging
from datetime import datetime

from assethub.core.config import config
from assethub.core.models import Asset, get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define supported file extensions by type
SUPPORTED_EXTENSIONS = {
    "model": [".obj", ".fbx", ".3ds", ".max", ".blend", ".dae", ".stl", ".ply"],
    "texture": [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".tga", ".hdr", ".exr"],
    "material": [".mtl", ".mat", ".xml", ".json"],
}

# Initialize mimetypes
mimetypes.init()


class AssetScanner:
    """Scanner for 3D assets in the filesystem."""

    def __init__(self):
        """Initialize the asset scanner."""
        self.session = get_session()
        self.scanned_files: Set[str] = set()
        self.new_assets: List[Asset] = []
        self.updated_assets: List[Asset] = []

    def scan_directory(self, directory_path: str, recursive: bool = True) -> Tuple[int, int]:
        """
        Scan a directory for 3D assets.

        Args:
            directory_path: Path to the directory to scan
            recursive: Whether to scan subdirectories recursively

        Returns:
            Tuple of (new_assets_count, updated_assets_count)
        """
        directory_path = os.path.abspath(os.path.expanduser(directory_path))
        logger.info(f"Scanning directory: {directory_path}")

        if not os.path.exists(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return 0, 0

        self.scanned_files = set()
        self.new_assets = []
        self.updated_assets = []

        # Walk through the directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                self._process_file(file_path)

            if not recursive:
                break

        # Save new and updated assets to the database
        self._save_assets()

        return len(self.new_assets), len(self.updated_assets)

    def _process_file(self, file_path: str) -> None:
        """
        Process a file and add it to the catalog if it's a supported asset.

        Args:
            file_path: Path to the file to process
        """
        # Skip if already processed
        if file_path in self.scanned_files:
            return
        
        self.scanned_files.add(file_path)
        
        # Check if the file is a supported asset
        file_ext = os.path.splitext(file_path)[1].lower()
        asset_type = self._get_asset_type(file_ext)
        
        if not asset_type:
            return
        
        # Check if the asset already exists in the database
        existing_asset = self.session.query(Asset).filter_by(file_path=file_path).first()
        
        # Get file stats
        try:
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            file_mtime = datetime.fromtimestamp(file_stats.st_mtime)
        except OSError as e:
            logger.error(f"Error getting file stats for {file_path}: {e}")
            return
        
        if existing_asset:
            # Check if the file has been modified
            if existing_asset.file_size != file_size or existing_asset.updated_at < file_mtime:
                self._update_asset(existing_asset, file_path, file_size, asset_type, file_ext)
        else:
            # Create a new asset
            self._create_asset(file_path, file_size, asset_type, file_ext)

    def _get_asset_type(self, file_ext: str) -> Optional[str]:
        """
        Determine the asset type based on file extension.

        Args:
            file_ext: File extension

        Returns:
            Asset type or None if not supported
        """
        for asset_type, extensions in SUPPORTED_EXTENSIONS.items():
            if file_ext in extensions:
                return asset_type
        return None

    def _create_asset(self, file_path: str, file_size: int, asset_type: str, file_ext: str) -> None:
        """
        Create a new asset.

        Args:
            file_path: Path to the asset file
            file_size: Size of the file in bytes
            asset_type: Type of the asset (model, texture, material)
            file_ext: File extension
        """
        file_name = os.path.basename(file_path)
        
        asset = Asset(
            name=file_name,
            description="",
            file_path=file_path,
            file_size=file_size,
            file_type=asset_type,
            file_format=file_ext[1:],  # Remove the dot
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            source="local"
        )
        
        # Extract additional metadata based on asset type
        if asset_type == "model":
            # TODO: Extract model-specific metadata (vertex count, face count, etc.)
            pass
        elif asset_type == "texture":
            # TODO: Extract texture-specific metadata (width, height, channels, etc.)
            pass
        
        self.new_assets.append(asset)

    def _update_asset(self, asset: Asset, file_path: str, file_size: int, asset_type: str, file_ext: str) -> None:
        """
        Update an existing asset.

        Args:
            asset: Asset to update
            file_path: Path to the asset file
            file_size: Size of the file in bytes
            asset_type: Type of the asset (model, texture, material)
            file_ext: File extension
        """
        asset.file_size = file_size
        asset.updated_at = datetime.utcnow()
        
        # Extract additional metadata based on asset type
        if asset_type == "model":
            # TODO: Extract model-specific metadata (vertex count, face count, etc.)
            pass
        elif asset_type == "texture":
            # TODO: Extract texture-specific metadata (width, height, channels, etc.)
            pass
        
        self.updated_assets.append(asset)

    def _save_assets(self) -> None:
        """Save new and updated assets to the database."""
        try:
            # Add new assets
            for asset in self.new_assets:
                self.session.add(asset)
            
            # Commit changes
            self.session.commit()
            
            logger.info(f"Added {len(self.new_assets)} new assets, updated {len(self.updated_assets)} assets")
        except Exception as e:
            logger.error(f"Error saving assets to database: {e}")
            self.session.rollback()
