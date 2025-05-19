"""
Asset search module for AssetHub.

This module provides functionality for searching assets.
"""
import logging
from typing import List, Dict, Any, Optional

from assethub.core.models import Asset
from assethub.catalog.indexer import Indexer

logger = logging.getLogger(__name__)

class AssetSearch:
    """Search engine for finding assets."""
    
    def __init__(self):
        """Initialize the search engine."""
        self.indexer = Indexer()
        self.indexer.create_index()
        
    def search(self, query: str, **filters) -> List[Asset]:
        """Search for assets.
        
        Args:
            query: Search query
            **filters: Additional filters
            
        Returns:
            List of matching assets
        """
        try:
            # Get all assets
            assets = list(self.indexer.index.assets.values())
            
            # Filter by query
            if query:
                query = query.lower()
                assets = [
                    asset for asset in assets
                    if query in asset.name.lower() or
                    any(query in tag.lower() for tag in asset.tags) or
                    any(query in category.lower() for category in asset.categories)
                ]
            
            # Apply additional filters
            assets = self._apply_filters(assets, filters)
            
            logger.info(f"Found {len(assets)} assets matching query: {query}")
            return assets
            
        except Exception as e:
            logger.error(f"Error searching assets: {str(e)}")
            return []
    
    def _apply_filters(self, assets: List[Asset], filters: Dict[str, Any]) -> List[Asset]:
        """Apply filters to assets.
        
        Args:
            assets: List of assets to filter
            filters: Filters to apply
            
        Returns:
            Filtered list of assets
        """
        filtered_assets = assets
        
        # Filter by asset type
        asset_type = filters.get("asset_type")
        if asset_type:
            filtered_assets = [
                asset for asset in filtered_assets
                if asset.file_type == asset_type
            ]
        
        # Filter by file format
        file_format = filters.get("file_format")
        if file_format:
            filtered_assets = [
                asset for asset in filtered_assets
                if asset.file_format == file_format
            ]
        
        # Filter by source
        source = filters.get("source")
        if source:
            filtered_assets = [
                asset for asset in filtered_assets
                if asset.source == source
            ]
        
        # Filter by categories
        categories = filters.get("categories")
        if categories and len(categories) > 0:
            filtered_assets = [
                asset for asset in filtered_assets
                if any(category in asset.categories for category in categories)
            ]
        
        return filtered_assets
