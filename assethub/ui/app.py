"""
Main application module for AssetHub GUI.

This module provides the main application window and UI components for AssetHub.
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QComboBox, QFileDialog,
    QListWidget, QListWidgetItem, QSplitter, QTabWidget,
    QTreeView, QMenu, QMessageBox, QProgressBar, QStatusBar
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QThread, QModelIndex
from PySide6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem

from assethub.core.config import config
from assethub.catalog.scanner import AssetScanner
from assethub.catalog.indexer import AssetIndexer
from assethub.catalog.search import AssetSearch
from assethub.integration import integration_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScanWorker(QThread):
    """Worker thread for scanning directories."""
    
    progress = Signal(int, int)  # new_assets, updated_assets
    finished = Signal()
    
    def __init__(self, directory: str, recursive: bool = True):
        """
        Initialize the scan worker.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
        """
        super().__init__()
        self.directory = directory
        self.recursive = recursive
        self.scanner = AssetScanner()
        
    def run(self):
        """Run the scan operation."""
        try:
            new_assets, updated_assets = self.scanner.scan_directory(
                self.directory, self.recursive
            )
            self.progress.emit(new_assets, updated_assets)
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
        finally:
            self.finished.emit()


class IndexWorker(QThread):
    """Worker thread for indexing assets."""
    
    progress = Signal(int)  # indexed_assets
    finished = Signal()
    
    def __init__(self, rebuild: bool = False):
        """
        Initialize the index worker.
        
        Args:
            rebuild: Whether to rebuild the index from scratch
        """
        super().__init__()
        self.rebuild = rebuild
        self.indexer = AssetIndexer()
        
    def run(self):
        """Run the indexing operation."""
        try:
            if self.rebuild:
                count = self.indexer.rebuild_index()
            else:
                # Index new assets
                from assethub.core.models import Asset, get_session
                session = get_session()
                assets = session.query(Asset).all()
                count = self.indexer.index_assets(assets)
            
            self.progress.emit(count)
        except Exception as e:
            logger.error(f"Error indexing assets: {e}")
        finally:
            self.finished.emit()


class SearchWorker(QThread):
    """Worker thread for searching assets."""
    
    results = Signal(list)
    finished = Signal()
    
    def __init__(self, query: str, filters: Optional[Dict[str, Any]] = None):
        """
        Initialize the search worker.
        
        Args:
            query: Search query
            filters: Search filters
        """
        super().__init__()
        self.query = query
        self.filters = filters or {}
        self.search = AssetSearch()
        
    def run(self):
        """Run the search operation."""
        try:
            results = self.search.search(self.query, filters=self.filters)
            self.results.emit(results)
        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            self.results.emit([])
        finally:
            self.finished.emit()


class AssetHubMainWindow(QMainWindow):
    """Main window for AssetHub application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.setWindowTitle("AssetHub")
        self.setMinimumSize(1000, 700)
        
        # Initialize components
        self.init_ui()
        
        # Initialize search engine
        self.search = AssetSearch()
        
        # Initialize scanner and indexer
        self.scanner = AssetScanner()
        self.indexer = AssetIndexer()
        self.indexer.create_index()
        
        # Load initial data
        self.load_categories()
        self.load_file_types()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
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
        
        # Splitter for sidebar and content
        splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filters
        filters_label = QLabel("Filters")
        filters_label.setStyleSheet("font-weight: bold;")
        
        # Category filter
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        
        # File type filter
        file_type_label = QLabel("File Type:")
        self.file_type_combo = QComboBox()
        
        # Apply filters button
        self.apply_filters_button = QPushButton("Apply Filters")
        self.apply_filters_button.clicked.connect(self.on_search)
        
        # Add to sidebar
        sidebar_layout.addWidget(filters_label)
        sidebar_layout.addWidget(category_label)
        sidebar_layout.addWidget(self.category_combo)
        sidebar_layout.addWidget(file_type_label)
        sidebar_layout.addWidget(self.file_type_combo)
        sidebar_layout.addWidget(self.apply_filters_button)
        
        # Actions
        actions_label = QLabel("Actions")
        actions_label.setStyleSheet("font-weight: bold;")
        
        # Scan directory button
        self.scan_button = QPushButton("Scan Directory")
        self.scan_button.clicked.connect(self.on_scan_directory)
        
        # Rebuild index button
        self.rebuild_index_button = QPushButton("Rebuild Index")
        self.rebuild_index_button.clicked.connect(self.on_rebuild_index)
        
        # Add to sidebar
        sidebar_layout.addWidget(actions_label)
        sidebar_layout.addWidget(self.scan_button)
        sidebar_layout.addWidget(self.rebuild_index_button)
        
        # Add spacer to push everything to the top
        sidebar_layout.addStretch()
        
        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs for local and online assets
        self.tabs = QTabWidget()
        
        # Local assets tab
        local_tab = QWidget()
        local_layout = QVBoxLayout(local_tab)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(64, 64))
        self.results_list.itemDoubleClicked.connect(self.on_asset_double_clicked)
        
        local_layout.addWidget(self.results_list)
        
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
        
        # Add tabs
        self.tabs.addTab(local_tab, "Local Assets")
        self.tabs.addTab(online_tab, "Online Assets")
        
        content_layout.addWidget(self.tabs)
        
        # Add sidebar and content to splitter
        splitter.addWidget(sidebar)
        splitter.addWidget(content)
        
        # Set initial sizes
        splitter.setSizes([200, 800])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Set initial status
        self.status_bar.showMessage("Ready")
    
    def load_categories(self):
        """Load categories into the category filter."""
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        
        categories = self.search.get_categories()
        for category in categories:
            self.category_combo.addItem(category)
    
    def load_file_types(self):
        """Load file types into the file type filter."""
        self.file_type_combo.clear()
        self.file_type_combo.addItem("All Types")
        
        file_types = self.search.get_file_types()
        for file_type in file_types:
            self.file_type_combo.addItem(file_type)
    
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
        
        # Start search in a separate thread
        self.search_worker = SearchWorker(query, filters)
        self.search_worker.results.connect(self.on_search_results)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.start()
    
    @Slot(list)
    def on_search_results(self, results):
        """Handle search results."""
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
    def on_search_finished(self):
        """Handle search completion."""
        self.progress_bar.setVisible(False)
    
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
    
    @Slot()
    def on_scan_directory(self):
        """Handle scan directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Scan", str(Path.home())
        )
        
        if not directory:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Scanning directory: {directory}...")
        
        # Start scan in a separate thread
        self.scan_worker = ScanWorker(directory)
        self.scan_worker.progress.connect(self.on_scan_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.start()
    
    @Slot(int, int)
    def on_scan_progress(self, new_assets, updated_assets):
        """
        Handle scan progress.
        
        Args:
            new_assets: Number of new assets found
            updated_assets: Number of updated assets
        """
        self.status_bar.showMessage(
            f"Scan complete: {new_assets} new assets, {updated_assets} updated"
        )
        
        # If new assets were found, offer to index them
        if new_assets > 0 or updated_assets > 0:
            reply = QMessageBox.question(
                self, "Index Assets",
                f"Found {new_assets} new assets and {updated_assets} updated assets. Index them now?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.on_rebuild_index()
    
    @Slot()
    def on_scan_finished(self):
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
    
    @Slot()
    def on_rebuild_index(self):
        """Handle rebuild index button click."""
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Rebuilding search index...")
        
        # Start indexing in a separate thread
        self.index_worker = IndexWorker(rebuild=True)
        self.index_worker.progress.connect(self.on_index_progress)
        self.index_worker.finished.connect(self.on_index_finished)
        self.index_worker.start()
    
    @Slot(int)
    def on_index_progress(self, count):
        """
        Handle indexing progress.
        
        Args:
            count: Number of indexed assets
        """
        self.status_bar.showMessage(f"Indexed {count} assets")
        
        # Reload categories and file types
        self.load_categories()
        self.load_file_types()
    
    @Slot()
    def on_index_finished(self):
        """Handle indexing completion."""
        self.progress_bar.setVisible(False)
    
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
        
        # Show asset details
        self.show_asset_details(asset_data)
    
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
    
    def show_asset_details(self, asset_data):
        """
        Show details for a local asset.
        
        Args:
            asset_data: Asset data dictionary
        """
        # Create a simple message box with asset details
        details = f"Name: {asset_data.get('name', '')}\n"
        details += f"Type: {asset_data.get('file_type', '')}\n"
        details += f"Format: {asset_data.get('file_format', '')}\n"
        details += f"Path: {asset_data.get('file_path', '')}\n"
        details += f"Size: {asset_data.get('file_size', 0)} bytes\n"
        
        if asset_data.get('vertex_count'):
            details += f"Vertices: {asset_data.get('vertex_count')}\n"
        
        if asset_data.get('face_count'):
            details += f"Faces: {asset_data.get('face_count')}\n"
        
        QMessageBox.information(self, "Asset Details", details)
    
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


def run_app():
    """Run the AssetHub application."""
    app = QApplication(sys.argv)
    window = AssetHubMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
