"""
Integration module for AssetHub.

This module provides integration with external asset providers.
"""
import logging
import importlib
import os
from typing import Dict, List, Any

from assethub.integration.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# Dictionary to store provider instances
_providers = {}

def get_providers():
    """Get all available providers.
    
    Returns:
        dict: Dictionary of provider instances
    """
    global _providers
    
    # If providers are already loaded, return them
    if _providers:
        return _providers
    
    # Load providers
    _providers = {}
    
    # Try to load Poly Haven provider
    try:
        from assethub.integration.providers.polyhaven import PolyHavenProvider
        provider = PolyHavenProvider()
        _providers["polyhaven"] = provider
        logger.info(f"Registered provider: {provider.provider_name}")
    except ImportError:
        logger.warning("Poly Haven provider not available")
    except Exception as e:
        logger.error(f"Error loading Poly Haven provider: {str(e)}")
    
    # Try to load Free3D provider
    try:
        from assethub.integration.providers.free3d import Free3DProvider
        provider = Free3DProvider()
        _providers["free3d"] = provider
        logger.info(f"Registered provider: {provider.provider_name}")
    except ImportError:
        logger.warning("Free3D provider not available")
    except Exception as e:
        logger.error(f"Error loading Free3D provider: {str(e)}")
    
    # Try to load CGTrader provider (if available)
    try:
        from assethub.integration.providers.cgtrader import CGTraderProvider
        provider = CGTraderProvider()
        _providers["cgtrader"] = provider
        logger.info(f"Registered provider: {provider.provider_name}")
    except ImportError:
        logger.debug("CGTrader provider not available")
    except Exception as e:
        logger.error(f"Error loading CGTrader provider: {str(e)}")
    
    # Try to load Turbosquid provider (if available)
    try:
        from assethub.integration.providers.turbosquid import TurbosquidProvider
        provider = TurbosquidProvider()
        _providers["turbosquid"] = provider
        logger.info(f"Registered provider: {provider.provider_name}")
    except ImportError:
        logger.debug("Turbosquid provider not available")
    except Exception as e:
        logger.error(f"Error loading Turbosquid provider: {str(e)}")
    
    return _providers

def search_all_providers(query: str, asset_type: str = None, page: int = 1, page_size: int = 20):
    """Search for assets across all providers.
    
    Args:
        query: Search query string
        asset_type: Type of asset to search for
        page: Page number for pagination
        page_size: Number of results per page
        
    Returns:
        list: Combined search results from all providers
    """
    providers = get_providers()
    all_results = []
    
    for provider_id, provider in providers.items():
        try:
            # Connect to provider if not already connected
            if not hasattr(provider, 'session') or provider.session is None:
                provider.connect()
            
            # Search for assets
            results = provider.search(query, asset_type, page, page_size)
            
            # Convert results to Asset objects
            if "results" in results:
                for item in results["results"]:
                    try:
                        asset = provider.convert_to_asset(item)
                        all_results.append(asset)
                    except Exception as e:
                        logger.error(f"Error converting asset from {provider.provider_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error searching {provider.provider_name}: {str(e)}")
    
    return all_results

def get_asset_details(provider_id: str, asset_id: str):
    """Get detailed information about an asset from a specific provider.
    
    Args:
        provider_id: ID of the provider
        asset_id: ID of the asset
        
    Returns:
        dict: Asset details
    """
    providers = get_providers()
    
    if provider_id in providers:
        provider = providers[provider_id]
        
        # Connect to provider if not already connected
        if not hasattr(provider, 'session') or provider.session is None:
            provider.connect()
        
        # Get asset details
        return provider.get_asset_details(asset_id)
    else:
        logger.error(f"Provider {provider_id} not found")
        return {"error": f"Provider {provider_id} not found"}

def download_asset(provider_id: str, asset_id: str, destination_path: str, format: str = None):
    """Download an asset from a specific provider.
    
    Args:
        provider_id: ID of the provider
        asset_id: ID of the asset
        destination_path: Path where the asset should be saved
        format: Format of the asset to download
        
    Returns:
        str: Path to the downloaded asset, or None if download failed
    """
    providers = get_providers()
    
    if provider_id in providers:
        provider = providers[provider_id]
        
        # Connect to provider if not already connected
        if not hasattr(provider, 'session') or provider.session is None:
            provider.connect()
        
        # Download asset
        return provider.download_asset(asset_id, destination_path, format)
    else:
        logger.error(f"Provider {provider_id} not found")
        return None

def get_preview(provider_id: str, asset_id: str, destination_path: str):
    """Download a preview image for an asset from a specific provider.
    
    Args:
        provider_id: ID of the provider
        asset_id: ID of the asset
        destination_path: Path where the preview should be saved
        
    Returns:
        str: Path to the downloaded preview, or None if download failed
    """
    providers = get_providers()
    
    if provider_id in providers:
        provider = providers[provider_id]
        
        # Connect to provider if not already connected
        if not hasattr(provider, 'session') or provider.session is None:
            provider.connect()
        
        # Download preview
        return provider.get_preview(asset_id, destination_path)
    else:
        logger.error(f"Provider {provider_id} not found")
        return None

def get_categories(provider_id: str = None):
    """Get available categories from providers.
    
    Args:
        provider_id: ID of the provider, or None for all providers
        
    Returns:
        dict: Categories organized by provider
    """
    providers = get_providers()
    categories = {}
    
    if provider_id:
        # Get categories from specific provider
        if provider_id in providers:
            provider = providers[provider_id]
            
            # Connect to provider if not already connected
            if not hasattr(provider, 'session') or provider.session is None:
                provider.connect()
            
            # Get categories
            categories[provider_id] = provider.get_categories()
        else:
            logger.error(f"Provider {provider_id} not found")
    else:
        # Get categories from all providers
        for provider_id, provider in providers.items():
            try:
                # Connect to provider if not already connected
                if not hasattr(provider, 'session') or provider.session is None:
                    provider.connect()
                
                # Get categories
                categories[provider_id] = provider.get_categories()
            except Exception as e:
                logger.error(f"Error getting categories from {provider.provider_name}: {str(e)}")
    
    return categories
