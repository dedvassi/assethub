"""
Main application module for AssetHub.

This module provides the main application window and UI components
for the AssetHub application, with a modern design inspired by Hamster 3D.
"""
import os
import sys
import logging
import threading
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QComboBox, QScrollArea, 
    QFrame, QSplitter, QFileDialog, QMessageBox, QProgressBar,
    QTabWidget, QGridLayout, QCheckBox, QMenu, QToolBar,
    QSizePolicy, QSpacerItem, QToolButton, QStatusBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import (
    Qt, QSize, QThread, pyqtSignal, QTimer, QUrl, QRect, 
    QPoint, QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QFont, QPalette, QColor, QCursor, 
    QImage, QPainter, QBrush, QLinearGradient, QFontDatabase
)

from assethub.core.config import config
from assethub.core.models import Asset, Category, SearchIndex
from assethub.catalog.scanner import FileScanner
from assethub.catalog.indexer import Indexer
from assethub.catalog.search import AssetSearch
from assethub.integration import get_providers

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DARK_BG_COLOR = "#1E1E1E"
DARKER_BG_COLOR = "#141414"
ACCENT_COLOR = "#8C52FF"  # Purple accent color
ACCENT_COLOR_HOVER = "#9D6FFF"
TEXT_COLOR = "#FFFFFF"
SECONDARY_TEXT_COLOR = "#AAAAAA"
BORDER_COLOR = "#333333"
CARD_BG_COLOR = "#2A2A2A"
CARD_HOVER_COLOR = "#3A3A3A"
SIDEBAR_WIDTH = 250
CARD_WIDTH = 220
CARD_HEIGHT = 280
CARD_SPACING = 15
ANIMATION_DURATION = 200  # ms

# Asset type icons
ASSET_TYPE_ICONS = {
    "model": "icons/model.png",
    "texture": "icons/texture.png",
    "material": "icons/material.png",
    "hdri": "icons/hdri.png",
    "other": "icons/other.png"
}

class AssetCard(QFrame):
    """Card widget for displaying an asset."""
    
    clicked = pyqtSignal(object)
    
    def __init__(self, asset: Asset, parent=None):
        """Initialize the asset card.
        
        Args:
            asset: Asset to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.asset = asset
        self.is_hovered = False
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Set up the card appearance
        self.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
        self.setObjectName("assetCard")
        self.setStyleSheet(f"""
            #assetCard {{
                background-color: {CARD_BG_COLOR};
                border-radius: 8px;
                border: 1px solid {BORDER_COLOR};
            }}
            #assetCard:hover {{
                background-color: {CARD_HOVER_COLOR};
                border: 1px solid {ACCENT_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Preview image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(140)
        self.preview_label.setMaximumHeight(140)
        self.preview_label.setStyleSheet(f"""
            background-color: {DARKER_BG_COLOR};
            border-radius: 4px;
        """)
        
        # Load preview image if available
        if hasattr(self.asset, 'preview_path') and os.path.exists(self.asset.preview_path):
            pixmap = QPixmap(self.asset.preview_path)
            pixmap = pixmap.scaled(CARD_WIDTH - 20, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
        else:
            # Use placeholder based on asset type
            asset_type = self.asset.file_type if self.asset.file_type else "other"
            icon_path = ASSET_TYPE_ICONS.get(asset_type, ASSET_TYPE_ICONS["other"])
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(pixmap)
            else:
                self.preview_label.setText("No Preview")
        
        layout.addWidget(self.preview_label)
        
        # Asset name
        self.name_label = QLabel(self.asset.name)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.name_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {TEXT_COLOR};
        """)
        layout.addWidget(self.name_label)
        
        # Asset type and format
        type_format = f"{self.asset.file_type.capitalize()} • {self.asset.file_format.upper()}"
        self.type_label = QLabel(type_format)
        self.type_label.setStyleSheet(f"""
            font-size: 12px;
            color: {SECONDARY_TEXT_COLOR};
        """)
        layout.addWidget(self.type_label)
        
        # Source
        self.source_label = QLabel(f"Source: {self.asset.source}")
        self.source_label.setStyleSheet(f"""
            font-size: 12px;
            color: {SECONDARY_TEXT_COLOR};
        """)
        layout.addWidget(self.source_label)
        
        # Add spacer to push everything to the top
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Bottom row with buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(5)
        
        # Import button
        self.import_button = QPushButton("Import")
        self.import_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR_HOVER};
            }}
        """)
        bottom_layout.addWidget(self.import_button)
        
        # Details button
        self.details_button = QPushButton("Details")
        self.details_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                border-color: {ACCENT_COLOR};
                color: {ACCENT_COLOR};
            }}
        """)
        bottom_layout.addWidget(self.details_button)
        
        layout.addLayout(bottom_layout)
        
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.asset)
        super().mousePressEvent(event)


class AssetGridWidget(QScrollArea):
    """Widget for displaying a grid of assets."""
    
    def __init__(self, parent=None):
        """Initialize the asset grid widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.assets = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Set up the scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QScrollArea {{
                background-color: {DARK_BG_COLOR};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {DARKER_BG_COLOR};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ACCENT_COLOR};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Create container widget
        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {DARK_BG_COLOR};")
        
        # Create grid layout
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(CARD_SPACING, CARD_SPACING, CARD_SPACING, CARD_SPACING)
        self.grid_layout.setSpacing(CARD_SPACING)
        
        self.setWidget(self.container)
        
    def set_assets(self, assets: List[Asset]):
        """Set the assets to display.
        
        Args:
            assets: List of assets to display
        """
        # Clear existing assets
        self.assets = assets
        
        # Clear the grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add assets to the grid
        columns = max(1, (self.width() - 2 * CARD_SPACING) // (CARD_WIDTH + CARD_SPACING))
        for i, asset in enumerate(assets):
            row = i // columns
            col = i % columns
            
            card = AssetCard(asset)
            card.clicked.connect(self.on_asset_clicked)
            self.grid_layout.addWidget(card, row, col)
            
        # Add empty items to fill the grid
        if assets:
            for i in range(len(assets), (((len(assets) - 1) // columns) + 1) * columns):
                row = i // columns
                col = i % columns
                spacer = QWidget()
                spacer.setFixedSize(CARD_WIDTH, CARD_HEIGHT)
                spacer.setStyleSheet("background-color: transparent;")
                self.grid_layout.addWidget(spacer, row, col)
    
    def on_asset_clicked(self, asset):
        """Handle asset click event.
        
        Args:
            asset: Clicked asset
        """
        # Show asset details dialog
        pass
        
    def resizeEvent(self, event):
        """Handle resize event."""
        # Recalculate grid layout when widget is resized
        if self.assets:
            self.set_assets(self.assets)
        super().resizeEvent(event)


class SidebarWidget(QWidget):
    """Sidebar widget for filtering and navigation."""
    
    filter_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize the sidebar widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Set fixed width
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setStyleSheet(f"""
            background-color: {DARKER_BG_COLOR};
            border-right: 1px solid {BORDER_COLOR};
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Logo and title
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("AH")
            logo_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {ACCENT_COLOR};
                background-color: {DARK_BG_COLOR};
                border-radius: 16px;
                padding: 5px;
            """)
            logo_label.setFixedSize(32, 32)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout.addWidget(logo_label)
        
        title_label = QLabel("AssetHub")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {TEXT_COLOR};
        """)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        layout.addLayout(logo_layout)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search assets...")
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
        """)
        self.search_edit.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.search_edit)
        
        # Filters section
        filters_label = QLabel("Filters")
        filters_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {TEXT_COLOR};
        """)
        layout.addWidget(filters_label)
        
        # Asset type filter
        type_label = QLabel("Asset Type")
        type_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR};")
        layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("All Types", "")
        self.type_combo.addItem("3D Models", "model")
        self.type_combo.addItem("Textures", "texture")
        self.type_combo.addItem("Materials", "material")
        self.type_combo.addItem("HDRIs", "hdri")
        self.type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox:hover {{
                border: 1px solid {ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {BORDER_COLOR};
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                selection-background-color: {ACCENT_COLOR};
                selection-color: white;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        self.type_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.type_combo)
        
        # Format filter
        format_label = QLabel("Format")
        format_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR};")
        layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("All Formats", "")
        self.format_combo.addItem("FBX", "fbx")
        self.format_combo.addItem("OBJ", "obj")
        self.format_combo.addItem("Blender", "blend")
        self.format_combo.addItem("3ds Max", "max")
        self.format_combo.addItem("PNG", "png")
        self.format_combo.addItem("JPG", "jpg")
        self.format_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox:hover {{
                border: 1px solid {ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {BORDER_COLOR};
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                selection-background-color: {ACCENT_COLOR};
                selection-color: white;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        self.format_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.format_combo)
        
        # Source filter
        source_label = QLabel("Source")
        source_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR};")
        layout.addWidget(source_label)
        
        self.source_combo = QComboBox()
        self.source_combo.addItem("All Sources", "")
        self.source_combo.addItem("Local Library", "local")
        self.source_combo.addItem("Poly Haven", "Poly Haven")
        self.source_combo.addItem("Free3D", "Free3D")
        self.source_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox:hover {{
                border: 1px solid {ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {BORDER_COLOR};
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                selection-background-color: {ACCENT_COLOR};
                selection-color: white;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        self.source_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.source_combo)
        
        # Categories section
        categories_label = QLabel("Categories")
        categories_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {TEXT_COLOR};
            margin-top: 10px;
        """)
        layout.addWidget(categories_label)
        
        # Category checkboxes in a scroll area
        categories_scroll = QScrollArea()
        categories_scroll.setWidgetResizable(True)
        categories_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {DARKER_BG_COLOR};
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ACCENT_COLOR};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        categories_layout.setContentsMargins(0, 0, 0, 0)
        categories_layout.setSpacing(5)
        
        # Sample categories (will be populated dynamically)
        sample_categories = [
            "Furniture", "Architecture", "Characters", 
            "Vehicles", "Nature", "Electronics", 
            "Food", "Animals", "Sci-Fi"
        ]
        
        self.category_checkboxes = {}
        for category in sample_categories:
            checkbox = QCheckBox(category)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {TEXT_COLOR};
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 3px;
                    background-color: {DARK_BG_COLOR};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {ACCENT_COLOR};
                    border: 1px solid {ACCENT_COLOR};
                    image: url(icons/check.png);
                }}
                QCheckBox::indicator:hover {{
                    border: 1px solid {ACCENT_COLOR};
                }}
            """)
            checkbox.stateChanged.connect(self.on_filter_changed)
            categories_layout.addWidget(checkbox)
            self.category_checkboxes[category] = checkbox
        
        categories_layout.addStretch()
        categories_scroll.setWidget(categories_widget)
        layout.addWidget(categories_scroll)
        
        # Add spacer to push everything to the top
        layout.addStretch()
        
        # Settings button at the bottom
        self.settings_button = QPushButton("Settings")
        self.settings_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {SECONDARY_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 8px;
                text-align: left;
            }}
            QPushButton:hover {{
                color: {TEXT_COLOR};
                border-color: {ACCENT_COLOR};
            }}
        """)
        layout.addWidget(self.settings_button)
        
    def on_filter_changed(self, *args):
        """Handle filter change events."""
        # Collect all filter values
        filters = {
            "search": self.search_edit.text(),
            "type": self.type_combo.currentData(),
            "format": self.format_combo.currentData(),
            "source": self.source_combo.currentData(),
            "categories": [cat for cat, cb in self.category_checkboxes.items() if cb.isChecked()]
        }
        
        # Emit signal with filter values
        self.filter_changed.emit(filters)


class AssetHubMainWindow(QMainWindow):
    """Main window for the AssetHub application."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize components
        self.indexer = Indexer()
        self.search = AssetSearch()
        self.providers = get_providers()
        
        # Create search index if it doesn't exist
        self.indexer.create_index()
        
        # Set up the UI
        self.setup_ui()
        
        # Load initial assets
        self.load_assets()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Set window properties
        self.setWindowTitle("AssetHub")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {DARK_BG_COLOR};
            }}
        """)
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.filter_changed.connect(self.apply_filters)
        main_layout.addWidget(self.sidebar)
        
        # Create right side container
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Create toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet(f"""
            background-color: {DARKER_BG_COLOR};
            border-bottom: 1px solid {BORDER_COLOR};
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 0, 15, 0)
        
        # View mode buttons
        view_group_layout = QHBoxLayout()
        view_group_layout.setSpacing(1)
        
        self.grid_view_button = QPushButton("Grid")
        self.grid_view_button.setCheckable(True)
        self.grid_view_button.setChecked(True)
        self.grid_view_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BG_COLOR};
                color: {SECONDARY_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 0;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                padding: 5px 15px;
            }}
            QPushButton:checked {{
                background-color: {ACCENT_COLOR};
                color: white;
                border-color: {ACCENT_COLOR};
            }}
            QPushButton:hover:!checked {{
                color: {TEXT_COLOR};
            }}
        """)
        view_group_layout.addWidget(self.grid_view_button)
        
        self.list_view_button = QPushButton("List")
        self.list_view_button.setCheckable(True)
        self.list_view_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BG_COLOR};
                color: {SECONDARY_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 0;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                padding: 5px 15px;
            }}
            QPushButton:checked {{
                background-color: {ACCENT_COLOR};
                color: white;
                border-color: {ACCENT_COLOR};
            }}
            QPushButton:hover:!checked {{
                color: {TEXT_COLOR};
            }}
        """)
        view_group_layout.addWidget(self.list_view_button)
        
        toolbar_layout.addLayout(view_group_layout)
        
        # Sort options
        sort_label = QLabel("Sort by:")
        sort_label.setStyleSheet(f"color: {SECONDARY_TEXT_COLOR};")
        toolbar_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Name (A-Z)")
        self.sort_combo.addItem("Name (Z-A)")
        self.sort_combo.addItem("Newest First")
        self.sort_combo.addItem("Oldest First")
        self.sort_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border: 1px solid {ACCENT_COLOR};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {BORDER_COLOR};
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_BG_COLOR};
                color: {TEXT_COLOR};
                selection-background-color: {ACCENT_COLOR};
                selection-color: white;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        toolbar_layout.addWidget(self.sort_combo)
        
        # Add spacer
        toolbar_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {SECONDARY_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                color: {TEXT_COLOR};
                border-color: {ACCENT_COLOR};
            }}
        """)
        self.refresh_button.clicked.connect(self.load_assets)
        toolbar_layout.addWidget(self.refresh_button)
        
        # Import local button
        self.import_button = QPushButton("Import Local")
        self.import_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR_HOVER};
            }}
        """)
        self.import_button.clicked.connect(self.import_local_assets)
        toolbar_layout.addWidget(self.import_button)
        
        right_layout.addWidget(toolbar)
        
        # Create asset grid
        self.asset_grid = AssetGridWidget()
        right_layout.addWidget(self.asset_grid)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {DARKER_BG_COLOR};
                color: {SECONDARY_TEXT_COLOR};
                border-top: 1px solid {BORDER_COLOR};
            }}
        """)
        self.setStatusBar(self.status_bar)
        
        # Add right container to main layout
        main_layout.addWidget(right_container)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
    def load_assets(self):
        """Load assets from the index."""
        try:
            # Show loading status
            self.status_bar.showMessage("Loading assets...")
            
            # Get all assets from the index
            assets = self.search.search("")
            
            # Update the asset grid
            self.asset_grid.set_assets(assets)
            
            # Update status bar
            self.status_bar.showMessage(f"Loaded {len(assets)} assets")
            
        except Exception as e:
            logger.error(f"Error loading assets: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load assets: {str(e)}")
            self.status_bar.showMessage("Error loading assets")
    
    def apply_filters(self, filters):
        """Apply filters to the asset list.
        
        Args:
            filters: Dictionary of filter values
        """
        try:
            # Show loading status
            self.status_bar.showMessage("Filtering assets...")
            
            # Build search query
            query = filters["search"]
            
            # Get filtered assets
            assets = self.search.search(
                query, 
                asset_type=filters["type"], 
                file_format=filters["format"],
                source=filters["source"],
                categories=filters["categories"]
            )
            
            # Update the asset grid
            self.asset_grid.set_assets(assets)
            
            # Update status bar
            self.status_bar.showMessage(f"Found {len(assets)} assets")
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to apply filters: {str(e)}")
            self.status_bar.showMessage("Error filtering assets")
    
    def import_local_assets(self):
        """Import assets from local directory."""
        try:
            # Show file dialog to select directory
            directory = QFileDialog.getExistingDirectory(
                self, "Select Directory", "", QFileDialog.Option.ShowDirsOnly
            )
            
            if directory:
                # Show progress dialog
                progress_dialog = QMessageBox(self)
                progress_dialog.setWindowTitle("Importing Assets")
                progress_dialog.setText("Scanning directory for assets...")
                progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
                progress_dialog.show()
                
                # Process events to update UI
                QApplication.processEvents()
                
                # Scan directory for assets
                scanner = FileScanner()
                assets = scanner.scan_directory(directory)
                
                # Update progress
                progress_dialog.setText(f"Found {len(assets)} assets. Indexing...")
                QApplication.processEvents()
                
                # Index assets
                for asset in assets:
                    self.indexer.add_asset(asset)
                
                # Close progress dialog
                progress_dialog.close()
                
                # Reload assets
                self.load_assets()
                
                # Show success message
                QMessageBox.information(
                    self, 
                    "Import Complete", 
                    f"Successfully imported {len(assets)} assets."
                )
                
        except Exception as e:
            logger.error(f"Error importing assets: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to import assets: {str(e)}")
            self.status_bar.showMessage("Error importing assets")


def run_app():
    """Run the AssetHub application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(DARK_BG_COLOR))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_COLOR))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(DARKER_BG_COLOR))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DARK_BG_COLOR))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(DARK_BG_COLOR))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT_COLOR))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_COLOR))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(DARK_BG_COLOR))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_COLOR))
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(ACCENT_COLOR))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT_COLOR))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(dark_palette)
    
    # Create and show main window
    main_window = AssetHubMainWindow()
    main_window.show()
    
    # Run application
    return app.exec()
