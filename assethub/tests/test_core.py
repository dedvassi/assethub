"""
Test module for AssetHub core functionality.

This module provides tests for the core functionality of AssetHub.
"""
import os
import unittest
import tempfile
import shutil
from pathlib import Path

from assethub.core.config import Config
from assethub.core.models import init_db, Asset, Tag, Category, get_session
from assethub.catalog.scanner import AssetScanner
from assethub.catalog.indexer import AssetIndexer
from assethub.catalog.search import AssetSearch


class TestAssetHubCore(unittest.TestCase):
    """Test case for AssetHub core functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        
        # Create test config
        self.config_path = os.path.join(self.test_dir, "config.json")
        self.config = Config(self.config_path)
        
        # Override config paths
        self.config.set("database", "path", os.path.join(self.test_dir, "test.db"))
        self.config.set("storage", "local_path", os.path.join(self.test_dir, "assets"))
        self.config.set("search", "index_path", os.path.join(self.test_dir, "index"))
        
        # Initialize database
        self.engine = init_db()
        self.session = get_session()
        
        # Create test assets directory
        self.assets_dir = os.path.join(self.test_dir, "test_assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Create test files
        self.create_test_files()
        
        # Initialize scanner, indexer, and search
        self.scanner = AssetScanner()
        self.indexer = AssetIndexer()
        self.search = AssetSearch()
    
    def tearDown(self):
        """Clean up test environment."""
        # Close session
        self.session.close()
        
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test files for scanning."""
        # Create model files
        model_dir = os.path.join(self.assets_dir, "models")
        os.makedirs(model_dir, exist_ok=True)
        
        with open(os.path.join(model_dir, "cube.obj"), "w") as f:
            f.write("# Test OBJ file")
        
        with open(os.path.join(model_dir, "sphere.fbx"), "w") as f:
            f.write("# Test FBX file")
        
        # Create texture files
        texture_dir = os.path.join(self.assets_dir, "textures")
        os.makedirs(texture_dir, exist_ok=True)
        
        with open(os.path.join(texture_dir, "wood.jpg"), "w") as f:
            f.write("# Test JPG file")
        
        with open(os.path.join(texture_dir, "metal.png"), "w") as f:
            f.write("# Test PNG file")
    
    def test_config(self):
        """Test configuration functionality."""
        # Test getting and setting config values
        self.config.set("test", "key", "value")
        self.assertEqual(self.config.get("test", "key"), "value")
        
        # Test default values
        self.assertEqual(self.config.get("nonexistent", "key", "default"), "default")
        
        # Test saving and loading config
        self.config.save_config()
        new_config = Config(self.config_path)
        self.assertEqual(new_config.get("test", "key"), "value")
    
    def test_database(self):
        """Test database functionality."""
        # Create test data
        tag = Tag(name="test_tag", description="Test tag")
        category = Category(name="test_category", description="Test category")
        asset = Asset(
            name="test_asset",
            description="Test asset",
            file_path="/path/to/asset",
            file_size=1024,
            file_type="model",
            file_format="obj"
        )
        
        # Add relationships
        asset.tags.append(tag)
        asset.categories.append(category)
        
        # Save to database
        self.session.add(tag)
        self.session.add(category)
        self.session.add(asset)
        self.session.commit()
        
        # Query and verify
        queried_asset = self.session.query(Asset).filter_by(name="test_asset").first()
        self.assertIsNotNone(queried_asset)
        self.assertEqual(queried_asset.name, "test_asset")
        self.assertEqual(queried_asset.file_type, "model")
        self.assertEqual(len(queried_asset.tags), 1)
        self.assertEqual(queried_asset.tags[0].name, "test_tag")
        self.assertEqual(len(queried_asset.categories), 1)
        self.assertEqual(queried_asset.categories[0].name, "test_category")
    
    def test_scanner(self):
        """Test asset scanner functionality."""
        # Scan test directory
        new_assets, updated_assets = self.scanner.scan_directory(self.assets_dir)
        
        # Verify results
        self.assertEqual(new_assets, 4)  # 2 models + 2 textures
        self.assertEqual(updated_assets, 0)
        
        # Verify database entries
        models = self.session.query(Asset).filter_by(file_type="model").all()
        textures = self.session.query(Asset).filter_by(file_type="texture").all()
        
        self.assertEqual(len(models), 2)
        self.assertEqual(len(textures), 2)
        
        # Scan again to test update
        new_assets, updated_assets = self.scanner.scan_directory(self.assets_dir)
        self.assertEqual(new_assets, 0)
        self.assertEqual(updated_assets, 0)
    
    def test_indexer(self):
        """Test asset indexer functionality."""
        # Scan test directory first
        self.scanner.scan_directory(self.assets_dir)
        
        # Create index
        self.indexer.create_index()
        
        # Rebuild index
        count = self.indexer.rebuild_index()
        
        # Verify results
        self.assertEqual(count, 4)  # 2 models + 2 textures
    
    def test_search(self):
        """Test asset search functionality."""
        # Scan and index test directory first
        self.scanner.scan_directory(self.assets_dir)
        self.indexer.create_index()
        self.indexer.rebuild_index()
        
        # Search for models
        results = self.search.search("cube")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "cube.obj")
        
        # Search with filters
        results = self.search.search("", filters={"file_type": "model"})
        self.assertEqual(len(results), 2)
        
        results = self.search.search("", filters={"file_type": "texture"})
        self.assertEqual(len(results), 2)
        
        # Search for non-existent asset
        results = self.search.search("nonexistent")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
