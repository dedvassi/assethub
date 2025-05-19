"""
Integration with Poly Haven free 3D asset library.

This module provides a provider for accessing the Poly Haven library,
which offers free HDRIs, textures, and 3D models.
"""
import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from assethub.integration.providers.base import BaseProvider
from assethub.core.config import config
from assethub.core.models import Asset

logger = logging.getLogger(__name__)

# Constants
POLYHAVEN_API_URL = "https://api.polyhaven.com"
POLYHAVEN_SITE_URL = "https://polyhaven.com"
POLYHAVEN_ASSET_TYPES = ["hdris", "textures", "models"]


class PolyHavenProvider(BaseProvider):
    """Provider for Poly Haven free 3D asset library."""
    
    def __init__(self):
        """Initialize the Poly Haven provider."""
        self.api_url = POLYHAVEN_API_URL
        self.site_url = POLYHAVEN_SITE_URL
        self.session = None
        self.provider_name = "Poly Haven"
        
    def connect(self):
        """Connect to Poly Haven API.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.session = requests.Session()
            # Test connection by getting a list of assets
            response = self.session.get(f"{self.api_url}/assets")
            response.raise_for_status()
            
            logger.info(f"Connected to {self.provider_name} API")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to {self.provider_name} API: {str(e)}")
            return False
        
    def search(self, query: str, asset_type: Optional[str] = None, page: int = 1, page_size: int = 20):
        """Search for assets in Poly Haven.
        
        Args:
            query: Search query string
            asset_type: Type of asset to search for (hdris, textures, models, or None for all)
            page: Page number for pagination
            page_size: Number of results per page
            
        Returns:
            dict: Search results with metadata
        """
        if not self.session:
            self.connect()
            
        try:
            # Get all assets first (Poly Haven API doesn't have direct search endpoint)
            response = self.session.get(f"{self.api_url}/assets")
            response.raise_for_status()
            all_assets = response.json()
            
            # Filter assets based on query and type
            filtered_assets = []
            for asset_id, asset_data in all_assets.items():
                # Filter by asset type if specified
                if asset_type and asset_data.get("type") != asset_type:
                    continue
                    
                # Simple search in asset ID and categories
                if (query.lower() in asset_id.lower() or 
                    any(query.lower() in cat.lower() for cat in asset_data.get("categories", []))):
                    # Add asset ID to the data for easier processing
                    asset_data["id"] = asset_id
                    filtered_assets.append(asset_data)
            
            # Sort by download count (popularity)
            filtered_assets.sort(key=lambda x: x.get("download_count", 0), reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_assets = filtered_assets[start_idx:end_idx]
            
            return {
                "results": paginated_assets,
                "total": len(filtered_assets),
                "page": page,
                "page_size": page_size
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching {self.provider_name}: {str(e)}")
            return {
                "results": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "error": str(e)
            }
        
    def get_asset_details(self, asset_id: str):
        """Get detailed information about an asset.
        
        Args:
            asset_id: ID of the asset to get details for
            
        Returns:
            dict: Asset details
        """
        if not self.session:
            self.connect()
            
        try:
            # Get asset details
            response = self.session.get(f"{self.api_url}/info/{asset_id}")
            response.raise_for_status()
            asset_info = response.json()
            
            # Add asset ID to the data
            asset_info["id"] = asset_id
            
            # Add download URLs
            asset_info["download_url"] = f"{self.site_url}/asset/{asset_id}"
            
            # Add preview URL
            asset_info["preview_url"] = f"{self.site_url}/files/renders/{asset_id}.png"
            
            return asset_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting asset details from {self.provider_name}: {str(e)}")
            return {"error": str(e)}
        
    def download_asset(self, asset_id: str, destination_path: str, format: str = "blend"):
        """Download an asset from Poly Haven.
        
        Args:
            asset_id: ID of the asset to download
            destination_path: Path where the asset should be saved
            format: Format of the asset to download (blend, fbx, obj, etc.)
            
        Returns:
            str: Path to the downloaded asset, or None if download failed
        """
        if not self.session:
            self.connect()
            
        try:
            # Get asset details to determine type and available formats
            asset_info = self.get_asset_details(asset_id)
            if "error" in asset_info:
                return None
                
            asset_type = asset_info.get("type")
            if not asset_type:
                logger.error(f"Unknown asset type for {asset_id}")
                return None
                
            # Determine download URL based on asset type
            if asset_type == "models":
                # For models, we need to get the specific format
                if format not in asset_info.get("files", {}).get(format, {}):
                    # If requested format is not available, use the first available format
                    available_formats = list(asset_info.get("files", {}).keys())
                    if not available_formats:
                        logger.error(f"No download formats available for {asset_id}")
                        return None
                    format = available_formats[0]
                
                # Get the highest resolution version
                resolutions = list(asset_info.get("files", {}).get(format, {}).keys())
                if not resolutions:
                    logger.error(f"No resolutions available for {asset_id} in {format} format")
                    return None
                    
                # Sort resolutions and get the highest
                resolution = sorted(resolutions)[-1]
                
                download_url = f"{self.site_url}/files/models/{format}/{asset_id}_{format}_{resolution}.zip"
                
            elif asset_type == "textures":
                # For textures, download the ZIP with all maps
                download_url = f"{self.site_url}/files/textures/{asset_id}/{asset_id}_4k.zip"
                
            elif asset_type == "hdris":
                # For HDRIs, download the highest resolution
                download_url = f"{self.site_url}/files/hdris/exr/{asset_id}_4k.exr"
                
            else:
                logger.error(f"Unsupported asset type: {asset_type}")
                return None
                
            # Download the file
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Save the file
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Downloaded {asset_id} to {destination_path}")
            return destination_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading asset from {self.provider_name}: {str(e)}")
            return None
        
    def get_preview(self, asset_id: str, destination_path: str):
        """Download a preview image for an asset.
        
        Args:
            asset_id: ID of the asset to get a preview for
            destination_path: Path where the preview should be saved
            
        Returns:
            str: Path to the downloaded preview, or None if download failed
        """
        if not self.session:
            self.connect()
            
        try:
            # Poly Haven has a consistent URL structure for previews
            preview_url = f"{self.site_url}/files/renders/{asset_id}.png"
            
            # Download the preview
            response = self.session.get(preview_url, stream=True)
            response.raise_for_status()
            
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Save the preview
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Downloaded preview for {asset_id} to {destination_path}")
            return destination_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading preview from {self.provider_name}: {str(e)}")
            return None
            
    def get_categories(self):
        """Get available categories from Poly Haven.
        
        Returns:
            dict: Categories organized by asset type
        """
        if not self.session:
            self.connect()
            
        try:
            # Get all assets to extract categories
            response = self.session.get(f"{self.api_url}/categories")
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting categories from {self.provider_name}: {str(e)}")
            return {}
            
    def convert_to_asset(self, item: Dict[str, Any]) -> Asset:
        """Convert a Poly Haven item to an Asset object.
        
        Args:
            item: Poly Haven asset data
            
        Returns:
            Asset: Converted Asset object
        """
        asset_id = item.get("id")
        asset_type = item.get("type", "")
        
        # Map Poly Haven asset types to AssetHub types
        asset_type_mapping = {
            "models": "model",
            "textures": "texture",
            "hdris": "hdri"
        }
        
        file_type = asset_type_mapping.get(asset_type, "other")
        
        # Determine file format based on asset type
        file_format = ""
        if asset_type == "models":
            # Default to blend, but could be any format
            file_format = "blend"
        elif asset_type == "textures":
            file_format = "zip"  # Textures are provided as ZIP archives
        elif asset_type == "hdris":
            file_format = "exr"  # HDRIs are provided as EXR files
            
        # Create Asset object
        asset = Asset(
            name=asset_id.replace("_", " ").title(),
            description=item.get("name", ""),
            file_path="",  # Will be set when downloaded
            file_size=0,   # Will be set when downloaded
            file_type=file_type,
            file_format=file_format,
            source=self.provider_name,
            source_url=f"{self.site_url}/asset/{asset_id}",
            source_id=asset_id,
            preview_url=f"{self.site_url}/files/renders/{asset_id}.png",
            license="CC0",  # Poly Haven uses CC0 license for all assets
            author=item.get("authors", {}).get("name", "Poly Haven")
        )
        
        return asset
