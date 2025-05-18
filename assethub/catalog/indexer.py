"""
Indexer module for AssetHub.

This module provides functionality to index assets for fast searching.
"""
import os
import shutil
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, ID, TEXT, KEYWORD, STORED, DATETIME, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring

from assethub.core.config import config
from assethub.core.models import Asset, SearchIndex, get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetIndexer:
    """Indexer for 3D assets."""

    def __init__(self):
        """Initialize the asset indexer."""
        self.session = get_session()
        self.index_path = config.get_index_path()
        self._ensure_index_dir()
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            name=TEXT(stored=True),
            description=TEXT,
            file_path=ID(stored=True),
            file_type=TEXT(stored=True),
            file_format=TEXT(stored=True),
            tags=KEYWORD(stored=True, commas=True, lowercase=True),
            categories=KEYWORD(stored=True, commas=True, lowercase=True),
            source=TEXT(stored=True),
            created_at=DATETIME(stored=True),
            updated_at=DATETIME(stored=True),
            file_size=NUMERIC(stored=True),
            vertex_count=NUMERIC(stored=True),
            face_count=NUMERIC(stored=True),
            width=NUMERIC(stored=True),
            height=NUMERIC(stored=True)
        )

    def _ensure_index_dir(self) -> None:
        """Ensure the index directory exists."""
        os.makedirs(self.index_path, exist_ok=True)

    def create_index(self) -> None:
        """Create a new search index."""
        if not exists_in(self.index_path):
            create_in(self.index_path, self.schema)
            logger.info(f"Created new search index at {self.index_path}")
            
            # Record index creation in database
            search_index = SearchIndex(
                path=str(self.index_path),
                last_updated=datetime.utcnow(),
                document_count=0
            )
            self.session.add(search_index)
            self.session.commit()
        else:
            logger.info(f"Search index already exists at {self.index_path}")

    def rebuild_index(self) -> int:
        """
        Rebuild the search index from scratch.

        Returns:
            Number of indexed assets
        """
        # Delete existing index
        if os.path.exists(self.index_path):
            shutil.rmtree(self.index_path)
            logger.info(f"Deleted existing index at {self.index_path}")
        
        # Create new index
        self._ensure_index_dir()
        self.create_index()
        
        # Index all assets
        assets = self.session.query(Asset).all()
        count = self.index_assets(assets)
        
        # Update index metadata
        search_index = self.session.query(SearchIndex).first()
        if search_index:
            search_index.last_updated = datetime.utcnow()
            search_index.document_count = count
            self.session.commit()
        
        return count

    def index_assets(self, assets: List[Asset]) -> int:
        """
        Index a list of assets.

        Args:
            assets: List of assets to index

        Returns:
            Number of indexed assets
        """
        if not assets:
            logger.info("No assets to index")
            return 0
        
        try:
            index = open_dir(self.index_path)
            writer = index.writer()
            
            count = 0
            for asset in assets:
                self._index_asset(writer, asset)
                count += 1
            
            writer.commit()
            logger.info(f"Indexed {count} assets")
            return count
        except Exception as e:
            logger.error(f"Error indexing assets: {e}")
            return 0

    def _index_asset(self, writer, asset: Asset) -> None:
        """
        Index a single asset.

        Args:
            writer: Index writer
            asset: Asset to index
        """
        # Prepare tags and categories as comma-separated strings
        tags = ",".join([tag.name for tag in asset.tags]) if asset.tags else ""
        categories = ",".join([category.name for category in asset.categories]) if asset.categories else ""
        
        # Add document to index
        writer.update_document(
            id=str(asset.id),
            name=asset.name,
            description=asset.description or "",
            file_path=asset.file_path,
            file_type=asset.file_type,
            file_format=asset.file_format,
            tags=tags,
            categories=categories,
            source=asset.source or "",
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            file_size=asset.file_size,
            vertex_count=asset.vertex_count or 0,
            face_count=asset.face_count or 0,
            width=asset.width or 0,
            height=asset.height or 0
        )

    def remove_asset(self, asset_id: int) -> bool:
        """
        Remove an asset from the index.

        Args:
            asset_id: ID of the asset to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            index = open_dir(self.index_path)
            writer = index.writer()
            writer.delete_by_term('id', str(asset_id))
            writer.commit()
            logger.info(f"Removed asset {asset_id} from index")
            return True
        except Exception as e:
            logger.error(f"Error removing asset {asset_id} from index: {e}")
            return False
