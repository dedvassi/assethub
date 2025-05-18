"""
Integration with Turbosquid library.

This module provides functionality to search and download assets from Turbosquid.
"""
import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from assethub.integration.providers.base import BaseProvider
from assethub.core.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Turbosquid API endpoints
TURBOSQUID_API_BASE = "https://api.turbosquid.com/v1/"
TURBOSQUID_SEARCH_ENDPOINT = "search"
TURBOSQUID_PRODUCT_ENDPOINT = "products/"


class TurbosquidProvider(BaseProvider):
    """Provider for Turbosquid 3D model library."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Turbosquid provider.

        Args:
            api_key: API key for Turbosquid (optional, can be set in config)
        """
        self.api_key = api_key or config.get("integration", "turbosquid_api_key")
        self.session = requests.Session()
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to Turbosquid API.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.api_key:
            logger.error("Turbosquid API key not provided")
            return False

        # Set up session headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # Test connection with a simple request
        try:
            response = self.session.get(urljoin(TURBOSQUID_API_BASE, "status"))
            if response.status_code == 200:
                self.connected = True
                logger.info("Connected to Turbosquid API")
                return True
            else:
                logger.error(f"Failed to connect to Turbosquid API: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to Turbosquid API: {e}")
            return False

    def search(self, query: str, asset_type: Optional[str] = None, 
               page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Search for assets in Turbosquid.

        Args:
            query: Search query string
            asset_type: Type of asset to search for (model, texture, material)
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            Dictionary containing search results and metadata
        """
        if not self.connected and not self.connect():
            return {"results": [], "total": 0, "page": page, "page_size": page_size}

        # Map asset_type to Turbosquid categories
        category = None
        if asset_type:
            category_map = {
                "model": "3d-models",
                "texture": "textures",
                "material": "materials"
            }
            category = category_map.get(asset_type)

        # Prepare search parameters
        params = {
            "q": query,
            "page": page,
            "per_page": page_size
        }

        if category:
            params["category"] = category

        try:
            response = self.session.get(
                urljoin(TURBOSQUID_API_BASE, TURBOSQUID_SEARCH_ENDPOINT),
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                
                # Transform response to standard format
                results = []
                for item in data.get("results", []):
                    results.append({
                        "id": str(item.get("id")),
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "preview_url": item.get("preview_image_url", ""),
                        "source": "turbosquid",
                        "source_url": item.get("url", ""),
                        "price": item.get("price", 0),
                        "currency": item.get("currency", "USD"),
                        "file_formats": item.get("file_formats", []),
                        "tags": item.get("tags", []),
                        "categories": item.get("categories", []),
                        "author": item.get("artist", {}).get("name", ""),
                        "created_at": item.get("created_at", ""),
                        "updated_at": item.get("updated_at", "")
                    })
                
                return {
                    "results": results,
                    "total": data.get("total_count", 0),
                    "page": page,
                    "page_size": page_size
                }
            else:
                logger.error(f"Error searching Turbosquid: {response.status_code}")
                return {"results": [], "total": 0, "page": page, "page_size": page_size}
        
        except Exception as e:
            logger.error(f"Error searching Turbosquid: {e}")
            return {"results": [], "total": 0, "page": page, "page_size": page_size}

    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an asset.

        Args:
            asset_id: ID of the asset in Turbosquid

        Returns:
            Dictionary containing asset details
        """
        if not self.connected and not self.connect():
            return {}

        try:
            response = self.session.get(
                urljoin(TURBOSQUID_API_BASE, f"{TURBOSQUID_PRODUCT_ENDPOINT}{asset_id}")
            )

            if response.status_code == 200:
                item = response.json()
                
                # Transform response to standard format
                return {
                    "id": str(item.get("id")),
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "preview_url": item.get("preview_image_url", ""),
                    "source": "turbosquid",
                    "source_url": item.get("url", ""),
                    "price": item.get("price", 0),
                    "currency": item.get("currency", "USD"),
                    "file_formats": item.get("file_formats", []),
                    "tags": item.get("tags", []),
                    "categories": item.get("categories", []),
                    "author": item.get("artist", {}).get("name", ""),
                    "created_at": item.get("created_at", ""),
                    "updated_at": item.get("updated_at", ""),
                    "vertex_count": item.get("vertex_count", 0),
                    "face_count": item.get("face_count", 0),
                    "is_rigged": item.get("is_rigged", False),
                    "is_animated": item.get("is_animated", False),
                    "is_pbr": item.get("is_pbr", False),
                    "is_uv_mapped": item.get("is_uv_mapped", False),
                    "dimensions": item.get("dimensions", {}),
                    "additional_images": item.get("additional_images", [])
                }
            else:
                logger.error(f"Error getting asset details from Turbosquid: {response.status_code}")
                return {}
        
        except Exception as e:
            logger.error(f"Error getting asset details from Turbosquid: {e}")
            return {}

    def download_asset(self, asset_id: str, destination_path: str) -> bool:
        """
        Download an asset from Turbosquid.

        Args:
            asset_id: ID of the asset in Turbosquid
            destination_path: Path where the asset should be saved

        Returns:
            True if download successful, False otherwise
        """
        if not self.connected and not self.connect():
            return False

        # Note: Actual implementation would require purchase flow and download API
        # This is a simplified version for demonstration purposes
        try:
            # Get download URL (in a real implementation, this would be the actual download URL)
            response = self.session.get(
                urljoin(TURBOSQUID_API_BASE, f"{TURBOSQUID_PRODUCT_ENDPOINT}{asset_id}/download")
            )

            if response.status_code == 200:
                download_url = response.json().get("download_url")
                
                if download_url:
                    # Download the file
                    download_response = self.session.get(download_url, stream=True)
                    
                    if download_response.status_code == 200:
                        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                        
                        with open(destination_path, 'wb') as f:
                            for chunk in download_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        logger.info(f"Downloaded asset {asset_id} to {destination_path}")
                        return True
                    else:
                        logger.error(f"Error downloading asset from Turbosquid: {download_response.status_code}")
                        return False
                else:
                    logger.error("Download URL not found")
                    return False
            else:
                logger.error(f"Error getting download URL from Turbosquid: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error downloading asset from Turbosquid: {e}")
            return False

    def get_preview(self, asset_id: str, destination_path: str) -> bool:
        """
        Download a preview image for an asset.

        Args:
            asset_id: ID of the asset in Turbosquid
            destination_path: Path where the preview image should be saved

        Returns:
            True if download successful, False otherwise
        """
        if not self.connected and not self.connect():
            return False

        try:
            # Get asset details to get preview URL
            asset_details = self.get_asset_details(asset_id)
            preview_url = asset_details.get("preview_url")
            
            if preview_url:
                # Download the preview image
                response = self.session.get(preview_url, stream=True)
                
                if response.status_code == 200:
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    
                    with open(destination_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    logger.info(f"Downloaded preview for asset {asset_id} to {destination_path}")
                    return True
                else:
                    logger.error(f"Error downloading preview from Turbosquid: {response.status_code}")
                    return False
            else:
                logger.error("Preview URL not found")
                return False
        
        except Exception as e:
            logger.error(f"Error downloading preview from Turbosquid: {e}")
            return False
