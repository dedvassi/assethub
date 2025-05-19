"""
Test module for AssetHub integration with free online libraries.

This module provides tests for the new providers and UI components.
"""
import os
import sys
import unittest
import logging
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import assethub modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assethub.integration.providers.polyhaven import PolyHavenProvider
from assethub.integration.providers.free3d import Free3DProvider
from assethub.integration import get_providers, search_all_providers


class TestPolyHavenProvider(unittest.TestCase):
    """Test cases for Poly Haven provider."""
    
    def setUp(self):
        """Set up test environment."""
        self.provider = PolyHavenProvider()
        
    def test_connect(self):
        """Test connection to Poly Haven API."""
        result = self.provider.connect()
        self.assertTrue(result, "Connection to Poly Haven API failed")
        
    def test_search(self):
        """Test search functionality."""
        # Connect to API
        self.provider.connect()
        
        # Search for assets
        results = self.provider.search("table")
        
        # Check if results are returned
        self.assertIsInstance(results, dict, "Search results should be a dictionary")
        self.assertIn("results", results, "Search results should contain 'results' key")
        self.assertIn("total", results, "Search results should contain 'total' key")
        
        # Check if results contain expected fields
        if results["results"]:
            first_result = results["results"][0]
            self.assertIn("id", first_result, "Result should contain 'id' field")
            
    def test_get_asset_details(self):
        """Test getting asset details."""
        # Connect to API
        self.provider.connect()
        
        # Search for assets to get an ID
        results = self.provider.search("table")
        
        # Check if results are returned
        if results["results"]:
            asset_id = results["results"][0]["id"]
            
            # Get asset details
            details = self.provider.get_asset_details(asset_id)
            
            # Check if details are returned
            self.assertIsInstance(details, dict, "Asset details should be a dictionary")
            self.assertIn("id", details, "Asset details should contain 'id' field")
            self.assertEqual(details["id"], asset_id, "Asset ID should match")
            
    def test_convert_to_asset(self):
        """Test converting API response to Asset object."""
        # Create a sample item
        item = {
            "id": "test_asset",
            "name": "Test Asset",
            "type": "models",
            "categories": ["furniture", "table"],
            "authors": {"name": "Test Author"}
        }
        
        # Convert to Asset object
        asset = self.provider.convert_to_asset(item)
        
        # Check Asset object properties
        self.assertEqual(asset.name, "Test Asset", "Asset name should match")
        self.assertEqual(asset.file_type, "model", "Asset type should be 'model'")
        self.assertEqual(asset.source, "Poly Haven", "Asset source should be 'Poly Haven'")
        self.assertEqual(asset.source_id, "test_asset", "Asset source ID should match")
        self.assertEqual(asset.license, "CC0", "Asset license should be 'CC0'")


class TestFree3DProvider(unittest.TestCase):
    """Test cases for Free3D provider."""
    
    def setUp(self):
        """Set up test environment."""
        self.provider = Free3DProvider()
        
    def test_connect(self):
        """Test connection to Free3D website."""
        result = self.provider.connect()
        self.assertTrue(result, "Connection to Free3D website failed")
        
    def test_search(self):
        """Test search functionality."""
        # Connect to website
        self.provider.connect()
        
        # Search for assets
        results = self.provider.search("chair")
        
        # Check if results are returned
        self.assertIsInstance(results, dict, "Search results should be a dictionary")
        self.assertIn("results", results, "Search results should contain 'results' key")
        self.assertIn("total", results, "Search results should contain 'total' key")
        
        # Check if results contain expected fields
        if results["results"]:
            first_result = results["results"][0]
            self.assertIn("id", first_result, "Result should contain 'id' field")
            self.assertIn("name", first_result, "Result should contain 'name' field")
            self.assertIn("url", first_result, "Result should contain 'url' field")
            
    def test_convert_to_asset(self):
        """Test converting API response to Asset object."""
        # Create a sample item
        item = {
            "id": "test_asset",
            "name": "Test Chair",
            "url": "https://free3d.com/3d-model/test_asset",
            "preview_url": "https://free3d.com/previews/test_asset.jpg",
            "formats": ["obj", "fbx"],
            "author": "Test Author",
            "license": "Free for personal use"
        }
        
        # Convert to Asset object
        asset = self.provider.convert_to_asset(item)
        
        # Check Asset object properties
        self.assertEqual(asset.name, "Test Chair", "Asset name should match")
        self.assertEqual(asset.file_type, "model", "Asset type should be 'model'")
        self.assertEqual(asset.source, "Free3D", "Asset source should be 'Free3D'")
        self.assertEqual(asset.source_id, "test_asset", "Asset source ID should match")
        self.assertEqual(asset.file_format, "obj", "Asset format should be the first format in the list")


class TestIntegration(unittest.TestCase):
    """Test cases for integration module."""
    
    def test_get_providers(self):
        """Test getting all providers."""
        providers = get_providers()
        
        # Check if providers are returned
        self.assertIsInstance(providers, dict, "Providers should be a dictionary")
        self.assertGreaterEqual(len(providers), 2, "At least two providers should be available")
        
        # Check if Poly Haven provider is available
        self.assertIn("polyhaven", providers, "Poly Haven provider should be available")
        
        # Check if Free3D provider is available
        self.assertIn("free3d", providers, "Free3D provider should be available")
        
    @patch('assethub.integration.providers.polyhaven.PolyHavenProvider.search')
    @patch('assethub.integration.providers.free3d.Free3DProvider.search')
    def test_search_all_providers(self, mock_free3d_search, mock_polyhaven_search):
        """Test searching across all providers."""
        # Mock search results
        mock_polyhaven_search.return_value = {
            "results": [
                {
                    "id": "ph_asset",
                    "name": "PH Test Asset",
                    "type": "models",
                    "categories": ["furniture"],
                    "authors": {"name": "Test Author"}
                }
            ],
            "total": 1
        }
        
        mock_free3d_search.return_value = {
            "results": [
                {
                    "id": "f3d_asset",
                    "name": "F3D Test Asset",
                    "url": "https://free3d.com/3d-model/f3d_asset",
                    "preview_url": "https://free3d.com/previews/f3d_asset.jpg",
                    "formats": ["obj"],
                    "author": "Test Author",
                    "license": "Free for personal use"
                }
            ],
            "total": 1
        }
        
        # Search all providers
        results = search_all_providers("test")
        
        # Check if results are returned
        self.assertIsInstance(results, list, "Search results should be a list")
        self.assertEqual(len(results), 2, "Two results should be returned")
        
        # Check if results contain assets from both providers
        sources = [asset.source for asset in results]
        self.assertIn("Poly Haven", sources, "Results should contain assets from Poly Haven")
        self.assertIn("Free3D", sources, "Results should contain assets from Free3D")


if __name__ == '__main__':
    unittest.main()
