"""
Base provider module for external asset libraries.

This module defines the base provider interface for integrating with external asset libraries.
"""
import abc
from typing import List, Dict, Any, Optional


class BaseProvider(abc.ABC):
    """Base class for external asset library providers."""

    @abc.abstractmethod
    def connect(self) -> bool:
        """
        Connect to the external library.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def search(self, query: str, asset_type: Optional[str] = None, 
               page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Search for assets in the external library.

        Args:
            query: Search query string
            asset_type: Type of asset to search for (model, texture, material)
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            Dictionary containing search results and metadata
        """
        pass

    @abc.abstractmethod
    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an asset.

        Args:
            asset_id: ID of the asset in the external library

        Returns:
            Dictionary containing asset details
        """
        pass

    @abc.abstractmethod
    def download_asset(self, asset_id: str, destination_path: str) -> bool:
        """
        Download an asset from the external library.

        Args:
            asset_id: ID of the asset in the external library
            destination_path: Path where the asset should be saved

        Returns:
            True if download successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_preview(self, asset_id: str, destination_path: str) -> bool:
        """
        Download a preview image for an asset.

        Args:
            asset_id: ID of the asset in the external library
            destination_path: Path where the preview image should be saved

        Returns:
            True if download successful, False otherwise
        """
        pass
