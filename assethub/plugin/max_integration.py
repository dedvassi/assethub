"""
3ds Max plugin integration for AssetHub.

This module provides functionality to integrate AssetHub with 3ds Max.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add parent directory to path to import AssetHub modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import MaxPlus for 3ds Max integration
try:
    import MaxPlus
except ImportError:
    # Mock MaxPlus for development outside of 3ds Max
    class MaxPlusMock:
        def FileManager_Reset(self):
            pass
            
        def FileManager_MergeFile(self, file_path):
            return True
            
        def NotificationManager_Register(self, code, callback):
            pass
            
    MaxPlus = MaxPlusMock()

# Import PySide for UI
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QComboBox, QTabWidget, QSplitter, QProgressBar, QStatusBar
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QPixmap

# Import AssetHub modules
from assethub.core.config import config
from assethub.catalog.search import AssetSearch
from assethub.integration import integration_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetHubMaxPlugin(QWidget):
    """AssetHub plugin for 3ds Max."""
    
    def __init__(self, parent=None):
        """Initialize the plugin."""
        super().__init__(parent)
        
        self.setWindowTitle("AssetHub for 3ds Max")
        self.setMinimumSize(800, 600)
        
        # Initialize UI
        self.init_ui()
        
        # Initialize search engine
        self.search = AssetSearch()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search assets...")
        self.search_input.returnPressed.connect(self.on_search)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        main_layout.addLayout(search_layout)
        
        # Tabs for local and online assets
        self.tabs = QTabWidget()
        
        # Local assets tab
        local_tab = QWidget()
        local_layout = QVBoxLayout(local_tab)
        
        # Filters
        filters_layout = QHBoxLayout()
        
        # Category filter
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        
        # File type filter
        file_type_label = QLabel("File Type:")
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItem("All Types")
        self.file_type_combo.addItem("model")
        self.file_type_combo.addItem("texture")
        self.file_type_combo.addItem("material")
        
        # Apply filters button
        self.apply_filters_button = QPushButton("Apply Filters")
        self.apply_filters_button.clicked.connect(self.on_search)
        
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(self.category_combo)
        filters_layout.addWidget(file_type_label)
        filters_layout.addWidget(self.file_type_combo)
        filters_layout.addWidget(self.apply_filters_button)
        
        local_layout.addLayout(filters_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(64, 64))
        self.results_list.itemDoubleClicked.connect(self.on_asset_double_clicked)
        
        local_layout.addWidget(self.results_list)
        
        # Import button
        self.import_button = QPushButton("Import Selected")
        self.import_button.clicked.connect(self.on_import_selected)
        local_layout.addWidget(self.import_button)
        
        # Online assets tab
        online_tab = QWidget()
        online_layout = QVBoxLayout(online_tab)
        
        # Provider selection
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Provider:")
        self.provider_combo = QComboBox()
        
        # Add available providers
        for provider in integration_manager.get_providers():
            self.provider_combo.addItem(provider)
        
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        
        # Online search button
        self.online_search_button = QPushButton("Search Online")
        self.online_search_button.clicked.connect(self.on_online_search)
        provider_layout.addWidget(self.online_search_button)
        
        online_layout.addLayout(provider_layout)
        
        # Online results list
        self.online_results_list = QListWidget()
        self.online_results_list.setIconSize(QSize(64, 64))
        self.online_results_list.itemDoubleClicked.connect(self.on_online_asset_double_clicked)
        
        online_layout.addWidget(self.online_results_list)
        
        # Download button
        self.download_button = QPushButton("Download Selected")
        self.download_button.clicked.connect(self.on_download_selected)
        online_layout.addWidget(self.download_button)
        
        # Add tabs
        self.tabs.addTab(local_tab, "Local Assets")
        self.tabs.addTab(online_tab, "Online Assets")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Set initial status
        self.status_bar.showMessage("Ready")
        
        # Load initial data
        self.load_categories()
    
    def load_categories(self):
        """Load categories into the category filter."""
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        
        categories = self.search.get_categories()
        for category in categories:
            self.category_combo.addItem(category)
    
    @Slot()
    def on_search(self):
        """Handle search button click."""
        query = self.search_input.text()
        
        # Get filters
        filters = {}
        
        category = self.category_combo.currentText()
        if category != "All Categories":
            filters["categories"] = category
        
        file_type = self.file_type_combo.currentText()
        if file_type != "All Types":
            filters["file_type"] = file_type
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Searching...")
        
        # Perform search
        try:
            results = self.search.search(query, filters=filters)
            self.display_results(results)
        except Exception as e:
            logger.error(f"Error searching: {e}")
            QMessageBox.warning(self, "Search Error", f"Error searching: {str(e)}")
        
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Ready")
    
    def display_results(self, results):
        """
        Display search results.
        
        Args:
            results: Search results
        """
        self.results_list.clear()
        
        for result in results:
            item = QListWidgetItem()
            item.setText(result.get("name", ""))
            item.setData(Qt.UserRole, result)
            
            # Set icon if preview is available
            preview_path = result.get("preview_path")
            if preview_path and os.path.exists(preview_path):
                icon = QIcon(preview_path)
                item.setIcon(icon)
            
            self.results_list.addItem(item)
        
        self.status_bar.showMessage(f"Found {len(results)} assets")
    
    @Slot()
    def on_online_search(self):
        """Handle online search button click."""
        query = self.search_input.text()
        provider = self.provider_combo.currentText()
        
        if not query:
            QMessageBox.warning(self, "Search Error", "Please enter a search query")
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Searching {provider}...")
        
        # Get provider
        provider_instance = integration_manager.get_provider(provider)
        
        if not provider_instance:
            QMessageBox.warning(self, "Provider Error", f"Provider {provider} not available")
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready")
            return
        
        # Connect to provider
        if not provider_instance.connect():
            QMessageBox.warning(self, "Connection Error", f"Could not connect to {provider}")
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready")
            return
        
        # Search
        try:
            results = provider_instance.search(query)
            self.display_online_results(results, provider)
        except Exception as e:
            logger.error(f"Error searching {provider}: {e}")
            QMessageBox.warning(self, "Search Error", f"Error searching {provider}: {str(e)}")
        
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Ready")
    
    def display_online_results(self, results, provider):
        """
        Display online search results.
        
        Args:
            results: Search results
            provider: Provider name
        """
        self.online_results_list.clear()
        
        result_items = results.get("results", [])
        
        for result in result_items:
            item = QListWidgetItem()
            item.setText(result.get("name", ""))
            
            # Add provider and ID to data
            result["provider"] = provider
            item.setData(Qt.UserRole, result)
            
            self.online_results_list.addItem(item)
        
        self.status_bar.showMessage(f"Found {len(result_items)} assets on {provider}")
    
    @Slot(QListWidgetItem)
    def on_asset_double_clicked(self, item):
        """
        Handle double-click on an asset.
        
        Args:
            item: Clicked list item
        """
        asset_data = item.data(Qt.UserRole)
        
        if not asset_data:
            return
        
        # Import the asset into 3ds Max
        self.import_asset(asset_data)
    
    @Slot()
    def on_import_selected(self):
        """Handle import selected button click."""
        selected_items = self.results_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Import Error", "No assets selected")
            return
        
        for item in selected_items:
            asset_data = item.data(Qt.UserRole)
            if asset_data:
                self.import_asset(asset_data)
    
    def import_asset(self, asset_data):
        """
        Import an asset into 3ds Max.
        
        Args:
            asset_data: Asset data dictionary
        """
        file_path = asset_data.get("file_path")
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Import Error", f"File not found: {file_path}")
            return
        
        # Check if the file is a 3D model
        file_type = asset_data.get("file_type")
        if file_type != "model":
            QMessageBox.warning(self, "Import Error", f"Cannot import {file_type} files")
            return
        
        # Import the file into 3ds Max
        try:
            # Reset file manager to avoid conflicts
            MaxPlus.FileManager_Reset()
            
            # Merge the file
            result = MaxPlus.FileManager_MergeFile(file_path)
            
            if result:
                self.status_bar.showMessage(f"Imported: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "Import Error", f"Failed to import: {file_path}")
        
        except Exception as e:
            logger.error(f"Error importing asset: {e}")
            QMessageBox.warning(self, "Import Error", f"Error importing asset: {str(e)}")
    
    @Slot(QListWidgetItem)
    def on_online_asset_double_clicked(self, item):
        """
        Handle double-click on an online asset.
        
        Args:
            item: Clicked list item
        """
        asset_data = item.data(Qt.UserRole)
        
        if not asset_data:
            return
        
        # Show asset details
        self.show_online_asset_details(asset_data)
    
    @Slot()
    def on_download_selected(self):
        """Handle download selected button click."""
        selected_items = self.online_results_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Download Error", "No assets selected")
            return
        
        # Get download directory
        download_dir = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", str(config.get_storage_path())
        )
        
        if not download_dir:
            return
        
        for item in selected_items:
            asset_data = item.data(Qt.UserRole)
            if asset_data:
                self.download_asset(asset_data, download_dir)
    
    def download_asset(self, asset_data, download_dir):
        """
        Download an asset.
        
        Args:
            asset_data: Asset data dictionary
            download_dir: Directory to download to
        """
        provider = asset_data.get("provider")
        asset_id = asset_data.get("id")
        
        if not provider or not asset_id:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Downloading from {provider}...")
        
        try:
            # Generate destination path
            asset_name = asset_data.get("name", "asset")
            # Sanitize filename
            asset_name = "".join(c for c in asset_name if c.isalnum() or c in " ._-").strip()
            destination_path = os.path.join(download_dir, f"{asset_name}.zip")
            
            # Download the asset
            success = integration_manager.download_asset(provider, asset_id, destination_path)
            
            if success:
                self.status_bar.showMessage(f"Downloaded to: {destination_path}")
                
                # Ask if user wants to import the downloaded asset
                reply = QMessageBox.question(
                    self, "Import Asset",
                    f"Asset downloaded successfully. Import it now?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    # TODO: Extract ZIP file and import the model
                    pass
            else:
                QMessageBox.warning(self, "Download Error", f"Failed to download from {provider}")
        
        except Exception as e:
            logger.error(f"Error downloading asset: {e}")
            QMessageBox.warning(self, "Download Error", f"Error downloading asset: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready")
    
    def show_online_asset_details(self, asset_data):
        """
        Show details for an online asset.
        
        Args:
            asset_data: Asset data dictionary
        """
        provider = asset_data.get("provider", "")
        asset_id = asset_data.get("id", "")
        
        if not provider or not asset_id:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Fetching details from {provider}...")
        
        try:
            # Get detailed information
            details = integration_manager.get_asset_details(provider, asset_id)
            
            if not details:
                QMessageBox.warning(self, "Error", f"Could not fetch details from {provider}")
                return
            
            # Create a simple message box with asset details
            details_text = f"Name: {details.get('name', '')}\n"
            details_text += f"Source: {provider}\n"
            
            if details.get('price'):
                details_text += f"Price: {details.get('price')} {details.get('currency', 'USD')}\n"
            
            if details.get('file_formats'):
                details_text += f"Formats: {', '.join(details.get('file_formats'))}\n"
            
            if details.get('vertex_count'):
                details_text += f"Vertices: {details.get('vertex_count')}\n"
            
            if details.get('face_count'):
                details_text += f"Faces: {details.get('face_count')}\n"
            
            if details.get('tags'):
                details_text += f"Tags: {', '.join(details.get('tags'))}\n"
            
            QMessageBox.information(self, "Asset Details", details_text)
            
        except Exception as e:
            logger.error(f"Error fetching details from {provider}: {e}")
            QMessageBox.warning(self, "Error", f"Error fetching details: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Ready")


def initialize_plugin():
    """Initialize the AssetHub plugin for 3ds Max."""
    # Create the plugin widget
    plugin_widget = AssetHubMaxPlugin()
    
    # Show the widget
    plugin_widget.show()
    
    return plugin_widget


# Entry point for 3ds Max
def dllexport():
    """Entry point for 3ds Max plugin."""
    return initialize_plugin()


if __name__ == "__main__":
    # For testing outside of 3ds Max
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    plugin = initialize_plugin()
    sys.exit(app.exec())
