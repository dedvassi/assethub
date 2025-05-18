"""
Search module for AssetHub.

This module provides functionality to search for assets in the index.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring
from whoosh.query import Term, And, Or, Not

from assethub.core.config import config
from assethub.core.models import Asset, get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetSearch:
    """Search engine for 3D assets."""

    def __init__(self):
        """Initialize the asset search engine."""
        self.session = get_session()
        self.index_path = config.get_index_path()

    def search(self, query_string: str, fields: Optional[List[str]] = None, 
               filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for assets matching the query.

        Args:
            query_string: Search query string
            fields: Fields to search in (default: name, description, tags, categories)
            filters: Additional filters to apply
            limit: Maximum number of results to return

        Returns:
            List of matching assets as dictionaries
        """
        if not os.path.exists(self.index_path):
            logger.error(f"Search index not found at {self.index_path}")
            return []
        
        try:
            index = open_dir(self.index_path)
            
            # Default fields to search in
            if fields is None:
                fields = ["name", "description", "tags", "categories"]
            
            # Create parser
            parser = MultifieldParser(fields, schema=index.schema)
            query = parser.parse(query_string)
            
            # Apply filters if provided
            if filters:
                filter_queries = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        # For list values, create OR query
                        or_queries = [Term(field, str(v)) for v in value]
                        filter_queries.append(Or(or_queries))
                    else:
                        filter_queries.append(Term(field, str(value)))
                
                if filter_queries:
                    query = And([query] + filter_queries)
            
            # Search
            with index.searcher(weighting=scoring.BM25F()) as searcher:
                results = searcher.search(query, limit=limit)
                
                # Convert results to dictionaries
                assets = []
                for result in results:
                    asset_dict = dict(result)
                    
                    # Convert datetime objects to strings
                    for key, value in asset_dict.items():
                        if isinstance(value, datetime):
                            asset_dict[key] = value.isoformat()
                    
                    assets.append(asset_dict)
                
                logger.info(f"Found {len(assets)} assets matching query: {query_string}")
                return assets
        
        except Exception as e:
            logger.error(f"Error searching for assets: {e}")
            return []

    def get_asset_by_id(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an asset by ID.

        Args:
            asset_id: ID of the asset to retrieve

        Returns:
            Asset as dictionary or None if not found
        """
        try:
            index = open_dir(self.index_path)
            with index.searcher() as searcher:
                result = searcher.document(id=str(asset_id))
                if result:
                    asset_dict = dict(result)
                    
                    # Convert datetime objects to strings
                    for key, value in asset_dict.items():
                        if isinstance(value, datetime):
                            asset_dict[key] = value.isoformat()
                    
                    return asset_dict
                return None
        except Exception as e:
            logger.error(f"Error retrieving asset {asset_id}: {e}")
            return None

    def get_tags(self) -> List[str]:
        """
        Get all unique tags in the index.

        Returns:
            List of unique tags
        """
        try:
            index = open_dir(self.index_path)
            with index.searcher() as searcher:
                return list(searcher.lexicon("tags"))
        except Exception as e:
            logger.error(f"Error retrieving tags: {e}")
            return []

    def get_categories(self) -> List[str]:
        """
        Get all unique categories in the index.

        Returns:
            List of unique categories
        """
        try:
            index = open_dir(self.index_path)
            with index.searcher() as searcher:
                return list(searcher.lexicon("categories"))
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            return []

    def get_file_types(self) -> List[str]:
        """
        Get all unique file types in the index.

        Returns:
            List of unique file types
        """
        try:
            index = open_dir(self.index_path)
            with index.searcher() as searcher:
                return list(searcher.lexicon("file_type"))
        except Exception as e:
            logger.error(f"Error retrieving file types: {e}")
            return []

    def get_file_formats(self) -> List[str]:
        """
        Get all unique file formats in the index.

        Returns:
            List of unique file formats
        """
        try:
            index = open_dir(self.index_path)
            with index.searcher() as searcher:
                return list(searcher.lexicon("file_format"))
        except Exception as e:
            logger.error(f"Error retrieving file formats: {e}")
            return []
