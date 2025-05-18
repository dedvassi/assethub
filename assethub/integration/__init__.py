"""
Integration module for AssetHub.

This module provides functionality to integrate with external asset libraries.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Type

from assethub.integration.providers.base import BaseProvider
from assethub.integration.providers.turbosquid import TurbosquidProvider
from assethub.integration.providers.cgtrader import CGTraderProvider
from assethub.core.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationManager:
    """Manager for external asset library integrations."""

    def __init__(self):
        """Initialize the integration manager."""
        self.providers: Dict[str, BaseProvider] = {}
        self._register_providers()

    def _register_providers(self) -> None:
        """Register available providers."""
        self.register_provider("turbosquid", TurbosquidProvider)
        self.register_provider("cgtrader", CGTraderProvider)

    def register_provider(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a provider.

        Args:
            name: Name of the provider
            provider_class: Provider class
        """
        try:
            # Get API key from config
            api_key = config.get("integration", f"{name}_api_key")
            
            # Initialize provider
            provider = provider_class(api_key=api_key)
            self.providers[name] = provider
            
            logger.info(f"Registered provider: {name}")
        except Exception as e:
            logger.error(f"Error registering provider {name}: {e}")

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """
        Get a provider by name.

        Args:
            name: Name of the provider

        Returns:
            Provider instance or None if not found
        """
        return self.providers.get(name)

    def get_providers(self) -> List[str]:
        """
        Get list of available providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def search_all(self, query: str, asset_type: Optional[str] = None, 
                  page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Search for assets in all registered providers.

        Args:
            query: Search query string
            asset_type: Type of asset to search for (model, texture, material)
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            Dictionary containing search results from all providers
        """
        results = {}
        
        for name, provider in self.providers.items():
            try:
                if provider.connect():
                    provider_results = provider.search(query, asset_type, page, page_size)
                    results[name] = provider_results
                else:
                    logger.warning(f"Could not connect to provider: {name}")
                    results[name] = {"results": [], "total": 0, "page": page, "page_size": page_size}
            except Exception as e:
                logger.error(f"Error searching provider {name}: {e}")
                results[name] = {"results": [], "total": 0, "page": page, "page_size": page_size}
        
        return results

    def download_asset(self, provider_name: str, asset_id: str, destination_path: str) -> bool:
        """
        Download an asset from a specific provider.

        Args:
            provider_name: Name of the provider
            asset_id: ID of the asset
            destination_path: Path where the asset should be saved

        Returns:
            True if download successful, False otherwise
        """
        provider = self.get_provider(provider_name)
        
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            return False
        
        if not provider.connect():
            logger.error(f"Could not connect to provider: {provider_name}")
            return False
        
        return provider.download_asset(asset_id, destination_path)

    def get_asset_details(self, provider_name: str, asset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an asset.

        Args:
            provider_name: Name of the provider
            asset_id: ID of the asset

        Returns:
            Dictionary containing asset details
        """
        provider = self.get_provider(provider_name)
        
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            return {}
        
        if not provider.connect():
            logger.error(f"Could not connect to provider: {provider_name}")
            return {}
        
        return provider.get_asset_details(asset_id)

    def get_preview(self, provider_name: str, asset_id: str, destination_path: str) -> bool:
        """
        Download a preview image for an asset.

        Args:
            provider_name: Name of the provider
            asset_id: ID of the asset
            destination_path: Path where the preview image should be saved

        Returns:
            True if download successful, False otherwise
        """
        provider = self.get_provider(provider_name)
        
        if not provider:
            logger.error(f"Provider not found: {provider_name}")
            return False
        
        if not provider.connect():
            logger.error(f"Could not connect to provider: {provider_name}")
            return False
        
        return provider.get_preview(asset_id, destination_path)


# Global integration manager instance
integration_manager = IntegrationManager()
