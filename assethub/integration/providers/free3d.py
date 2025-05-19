"""
Integration with Free3D free 3D asset library.

This module provides a provider for accessing the Free3D library,
which offers free 3D models in various formats.
"""
import os
import json
import logging
import requests
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from assethub.integration.providers.base import BaseProvider
from assethub.core.config import config
from assethub.core.models import Asset

logger = logging.getLogger(__name__)

# Constants
FREE3D_SITE_URL = "https://free3d.com"
FREE3D_SEARCH_URL = "https://free3d.com/search/"


class Free3DProvider(BaseProvider):
    """Provider for Free3D free 3D asset library."""
    
    def __init__(self):
        """Initialize the Free3D provider."""
        self.site_url = FREE3D_SITE_URL
        self.search_url = FREE3D_SEARCH_URL
        self.session = None
        self.provider_name = "Free3D"
        
    def connect(self):
        """Connect to Free3D website.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.session = requests.Session()
            # Test connection by accessing the main page
            response = self.session.get(self.site_url)
            response.raise_for_status()
            
            logger.info(f"Connected to {self.provider_name} website")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to {self.provider_name} website: {str(e)}")
            return False
        
    def search(self, query: str, asset_type: Optional[str] = None, page: int = 1, page_size: int = 20):
        """Search for assets in Free3D.
        
        Args:
            query: Search query string
            asset_type: Type of asset to search for (model, texture, etc.)
            page: Page number for pagination
            page_size: Number of results per page
            
        Returns:
            dict: Search results with metadata
        """
        if not self.session:
            self.connect()
            
        try:
            # Construct search URL
            search_query = query.replace(" ", "+")
            url = f"{self.search_url}{search_query}/"
            
            # Add page parameter if not the first page
            if page > 1:
                url += f"page-{page}/"
                
            # Add filter for free models only
            url += "?only=free"
            
            # Add filter for asset type if specified
            if asset_type:
                if asset_type == "model":
                    # No specific filter needed as all are models
                    pass
                elif asset_type == "blender":
                    url += "&file=blend"
                elif asset_type == "3dsmax":
                    url += "&file=max"
                elif asset_type == "maya":
                    url += "&file=ma"
                elif asset_type == "obj":
                    url += "&file=obj"
                elif asset_type == "fbx":
                    url += "&file=fbx"
            
            # Send request
            response = self.session.get(url)
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract results
            results = []
            model_items = soup.select('.model-item')
            
            for item in model_items:
                # Extract model information
                model_data = {}
                
                # Get model ID and name
                title_elem = item.select_one('.model-title a')
                if title_elem:
                    model_data['name'] = title_elem.text.strip()
                    model_data['url'] = urljoin(self.site_url, title_elem['href'])
                    # Extract ID from URL
                    model_id_match = re.search(r'/3d-model/([^/]+)', model_data['url'])
                    if model_id_match:
                        model_data['id'] = model_id_match.group(1)
                    else:
                        model_data['id'] = model_data['url'].split('/')[-2]
                
                # Get preview image
                img_elem = item.select_one('.model-img img')
                if img_elem and 'src' in img_elem.attrs:
                    model_data['preview_url'] = img_elem['src']
                
                # Get price (should be $0 for free models)
                price_elem = item.select_one('.model-price')
                if price_elem:
                    price_text = price_elem.text.strip()
                    model_data['price'] = price_text
                    model_data['is_free'] = 'Free' in price_text or '$0' in price_text
                
                # Get formats
                formats_elem = item.select_one('.model-formats')
                if formats_elem:
                    formats_text = formats_elem.text.strip()
                    model_data['formats'] = [fmt.strip().lower() for fmt in formats_text.split('.') if fmt.strip()]
                
                # Only add free models
                if model_data.get('is_free', False):
                    results.append(model_data)
            
            # Extract pagination information
            total_items = 0
            pagination_info = soup.select_one('.pagination-info')
            if pagination_info:
                pagination_text = pagination_info.text.strip()
                total_match = re.search(r'of (\d+)', pagination_text)
                if total_match:
                    total_items = int(total_match.group(1))
            
            return {
                "results": results[:page_size],  # Limit to requested page size
                "total": total_items,
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
        except Exception as e:
            logger.error(f"Error parsing {self.provider_name} search results: {str(e)}")
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
            # Construct asset URL
            url = f"{self.site_url}/3d-model/{asset_id}"
            
            # Send request
            response = self.session.get(url)
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract asset details
            asset_info = {
                'id': asset_id,
                'url': url
            }
            
            # Get asset name
            title_elem = soup.select_one('h1.model-title')
            if title_elem:
                asset_info['name'] = title_elem.text.strip()
            
            # Get asset description
            desc_elem = soup.select_one('.model-description')
            if desc_elem:
                asset_info['description'] = desc_elem.text.strip()
            
            # Get preview images
            preview_images = []
            img_elems = soup.select('.model-img-big img')
            for img in img_elems:
                if 'src' in img.attrs:
                    preview_images.append(img['src'])
            asset_info['preview_images'] = preview_images
            if preview_images:
                asset_info['preview_url'] = preview_images[0]
            
            # Get formats
            formats = []
            format_elems = soup.select('.model-formats span')
            for fmt in format_elems:
                format_text = fmt.text.strip().lower()
                if format_text and format_text not in formats:
                    formats.append(format_text)
            asset_info['formats'] = formats
            
            # Get author
            author_elem = soup.select_one('.model-author a')
            if author_elem:
                asset_info['author'] = author_elem.text.strip()
                asset_info['author_url'] = urljoin(self.site_url, author_elem['href'])
            
            # Get download information
            download_elem = soup.select_one('.model-download-btn')
            if download_elem and 'href' in download_elem.attrs:
                asset_info['download_url'] = urljoin(self.site_url, download_elem['href'])
            
            # Get license information
            license_elem = soup.select_one('.model-license')
            if license_elem:
                asset_info['license'] = license_elem.text.strip()
            else:
                # Default license for Free3D free models
                asset_info['license'] = "Free for personal use"
            
            return asset_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting asset details from {self.provider_name}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error parsing {self.provider_name} asset details: {str(e)}")
            return {"error": str(e)}
        
    def download_asset(self, asset_id: str, destination_path: str, format: Optional[str] = None):
        """Download an asset from Free3D.
        
        Args:
            asset_id: ID of the asset to download
            destination_path: Path where the asset should be saved
            format: Format of the asset to download (optional)
            
        Returns:
            str: Path to the downloaded asset, or None if download failed
        """
        if not self.session:
            self.connect()
            
        try:
            # Get asset details to find download URL
            asset_info = self.get_asset_details(asset_id)
            if "error" in asset_info:
                return None
                
            download_url = asset_info.get("download_url")
            if not download_url:
                logger.error(f"No download URL found for asset {asset_id}")
                return None
            
            # For Free3D, we need to follow the download link to get the actual file
            # This typically involves a download page with a countdown
            response = self.session.get(download_url)
            response.raise_for_status()
            
            # Parse the download page to find the actual download link
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the download button that appears after countdown
            final_download_elem = soup.select_one('#downloadBtn')
            if not final_download_elem or 'href' not in final_download_elem.attrs:
                logger.error(f"Could not find final download link for asset {asset_id}")
                return None
                
            final_download_url = urljoin(self.site_url, final_download_elem['href'])
            
            # Download the file
            response = self.session.get(final_download_url, stream=True)
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
        except Exception as e:
            logger.error(f"Error processing download from {self.provider_name}: {str(e)}")
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
            # Get asset details to find preview URL
            asset_info = self.get_asset_details(asset_id)
            if "error" in asset_info:
                return None
                
            preview_url = asset_info.get("preview_url")
            if not preview_url:
                logger.error(f"No preview URL found for asset {asset_id}")
                return None
                
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
        except Exception as e:
            logger.error(f"Error processing preview from {self.provider_name}: {str(e)}")
            return None
            
    def get_categories(self):
        """Get available categories from Free3D.
        
        Returns:
            list: List of category names
        """
        if not self.session:
            self.connect()
            
        try:
            # Access the main page to extract categories
            response = self.session.get(self.site_url)
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract categories
            categories = []
            category_elems = soup.select('.category-list a')
            for cat in category_elems:
                cat_name = cat.text.strip()
                if cat_name and cat_name not in categories:
                    categories.append(cat_name)
            
            return categories
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting categories from {self.provider_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing categories from {self.provider_name}: {str(e)}")
            return []
            
    def convert_to_asset(self, item: Dict[str, Any]) -> Asset:
        """Convert a Free3D item to an Asset object.
        
        Args:
            item: Free3D asset data
            
        Returns:
            Asset: Converted Asset object
        """
        asset_id = item.get("id", "")
        name = item.get("name", "")
        
        # Determine file format based on available formats
        formats = item.get("formats", [])
        file_format = formats[0] if formats else "zip"
            
        # Create Asset object
        asset = Asset(
            name=name,
            description=item.get("description", ""),
            file_path="",  # Will be set when downloaded
            file_size=0,   # Will be set when downloaded
            file_type="model",  # Free3D primarily offers models
            file_format=file_format,
            source=self.provider_name,
            source_url=item.get("url", f"{self.site_url}/3d-model/{asset_id}"),
            source_id=asset_id,
            preview_url=item.get("preview_url", ""),
            license=item.get("license", "Free for personal use"),
            author=item.get("author", "Unknown")
        )
        
        return asset
