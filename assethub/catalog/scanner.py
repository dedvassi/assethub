"""
Asset scanner module for AssetHub.

This module provides functionality for scanning directories for assets.
"""
import os
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from assethub.core.models import Asset
from assethub.core.config import config

logger = logging.getLogger(__name__)

class FileScanner:
    """Scanner for finding assets in directories."""
    
    def __init__(self):
        """Initialize the file scanner."""
        self.supported_formats = config["supported_formats"]
        
    def scan_directory(self, directory: str) -> List[Asset]:
        """Scan a directory for assets.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of assets found
        """
        logger.info(f"Scanning directory: {directory}")
        assets = []
        
        try:
            # Walk through directory
            for root, _, files in os.walk(directory):
                for file in files:
                    # Get file extension
                    _, ext = os.path.splitext(file)
                    ext = ext.lower().lstrip(".")
                    
                    # Check if file is a supported format
                    asset_type = self._get_asset_type(ext)
                    if asset_type:
                        # Create asset
                        file_path = os.path.join(root, file)
                        asset = self._create_asset(file_path, asset_type, ext)
                        assets.append(asset)
            
            logger.info(f"Found {len(assets)} assets in {directory}")
            return assets
            
        except Exception as e:
            logger.error(f"Error scanning directory: {str(e)}")
            return []
    
    def _get_asset_type(self, extension: str) -> Optional[str]:
        """Get asset type from file extension.
        
        Args:
            extension: File extension
            
        Returns:
            Asset type or None if not supported
        """
        for asset_type, formats in self.supported_formats.items():
            if extension in formats:
                return asset_type
        return None
    
    def _create_asset(self, file_path: str, asset_type: str, file_format: str) -> Asset:
        """Create an asset from a file.
        
        Args:
            file_path: Path to the file
            asset_type: Type of asset
            file_format: File format
            
        Returns:
            Asset object
        """
        # Get file name without extension
        file_name = os.path.basename(file_path)
        name, _ = os.path.splitext(file_name)
        
        # Generate ID from file path
        file_id = hashlib.md5(file_path.encode()).hexdigest()
        
        # Create asset
        asset = Asset(
            id=file_id,
            name=name,
            file_path=file_path,
            file_type=asset_type,
            file_format=file_format,
            source="local",
            categories=[],
            tags=[],
            metadata={
                "size": os.path.getsize(file_path),
                "modified": os.path.getmtime(file_path)
            }
        )
        
        return asset
