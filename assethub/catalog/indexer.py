"""
Asset indexer module for AssetHub.

This module provides functionality for indexing assets.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from assethub.core.models import Asset, SearchIndex
from assethub.core.config import config, get_index_file

logger = logging.getLogger(__name__)

class Indexer:
    """Indexer for managing the asset index."""
    
    def __init__(self):
        """Initialize the indexer."""
        self.index_file = get_index_file()
        self.index = SearchIndex()
        
    def create_index(self) -> bool:
        """Create or load the search index.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing index if it exists
            if os.path.exists(self.index_file):
                self.load_index()
            else:
                # Create new index
                self.save_index()
                
            return True
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            return False
    
    def load_index(self) -> bool:
        """Load the search index from file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.index_file, "r") as f:
                data = json.load(f)
                
                # Convert JSON to SearchIndex
                self.index = SearchIndex()
                
                # Load assets
                for asset_id, asset_data in data.get("assets", {}).items():
                    self.index.assets[asset_id] = Asset(**asset_data)
                
                # Load categories
                # (Simplified for this example)
                
                logger.info(f"Loaded {len(self.index.assets)} assets from index")
                return True
                
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False
    
    def save_index(self) -> bool:
        """Save the search index to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert SearchIndex to JSON-serializable dict
            data = {
                "assets": {asset_id: asset.__dict__ for asset_id, asset in self.index.assets.items()},
                "categories": {},  # Simplified for this example
                "tags": self.index.tags
            }
            
            # Save to file
            with open(self.index_file, "w") as f:
                json.dump(data, f, indent=4, default=str)
                
            logger.info(f"Saved {len(self.index.assets)} assets to index")
            return True
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            return False
    
    def add_asset(self, asset: Asset) -> bool:
        """Add an asset to the index.
        
        Args:
            asset: Asset to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add asset to index
            self.index.assets[asset.id] = asset
            
            # Add tags
            for tag in asset.tags:
                if tag not in self.index.tags:
                    self.index.tags[tag] = []
                self.index.tags[tag].append(asset.id)
            
            # Save index
            self.save_index()
            
            logger.info(f"Added asset to index: {asset.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding asset to index: {str(e)}")
            return False
    
    def remove_asset(self, asset_id: str) -> bool:
        """Remove an asset from the index.
        
        Args:
            asset_id: ID of asset to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if asset exists
            if asset_id not in self.index.assets:
                logger.warning(f"Asset not found in index: {asset_id}")
                return False
            
            # Get asset
            asset = self.index.assets[asset_id]
            
            # Remove asset from index
            del self.index.assets[asset_id]
            
            # Remove from tags
            for tag in asset.tags:
                if tag in self.index.tags and asset_id in self.index.tags[tag]:
                    self.index.tags[tag].remove(asset_id)
            
            # Save index
            self.save_index()
            
            logger.info(f"Removed asset from index: {asset.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing asset from index: {str(e)}")
            return False
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get an asset from the index.
        
        Args:
            asset_id: ID of asset to get
            
        Returns:
            Asset if found, None otherwise
        """
        return self.index.assets.get(asset_id)
