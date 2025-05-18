# AssetHub - Developer Guide

## Introduction

This developer guide provides detailed information for developers who want to contribute to AssetHub or extend its functionality. AssetHub is a resource management platform for 3ds Max designers, built with Python and designed with extensibility in mind.

## Project Structure

```
assethub_project/
├── assethub/
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   └── models.py      # Data models
│   ├── catalog/           # Asset cataloging and search
│   │   ├── scanner.py     # File scanner
│   │   ├── indexer.py     # Search indexer
│   │   └── search.py      # Search engine
│   ├── integration/       # External library integration
│   │   ├── providers/     # Provider implementations
│   │   │   ├── base.py    # Base provider interface
│   │   │   ├── turbosquid.py # Turbosquid provider
│   │   │   └── cgtrader.py # CGTrader provider
│   │   └── __init__.py    # Integration manager
│   ├── ui/                # User interface
│   │   └── app.py         # Main application
│   ├── plugin/            # 3ds Max plugin
│   │   └── max_integration.py # 3ds Max integration
│   └── tests/             # Unit tests
├── docs/                  # Documentation
├── main.py                # Application entry point
├── pyproject.toml         # Project metadata and dependencies
└── README.md              # Project overview
```

## Architecture

AssetHub follows a modular architecture with clear separation of concerns:

1. **Core Module**: Provides configuration management and data models
2. **Catalog Module**: Handles asset scanning, indexing, and searching
3. **Integration Module**: Manages integration with external libraries
4. **UI Module**: Implements the user interface
5. **Plugin Module**: Provides integration with 3ds Max

### Core Module

The core module provides the foundation for AssetHub:

- `config.py`: Manages application configuration
- `models.py`: Defines SQLAlchemy data models for assets, tags, categories, etc.

### Catalog Module

The catalog module handles asset management:

- `scanner.py`: Scans directories for assets and extracts metadata
- `indexer.py`: Indexes assets for fast searching using Whoosh
- `search.py`: Provides search functionality for indexed assets

### Integration Module

The integration module manages external library integration:

- `providers/base.py`: Defines the base provider interface
- `providers/turbosquid.py`: Implements the Turbosquid provider
- `providers/cgtrader.py`: Implements the CGTrader provider
- `__init__.py`: Provides the integration manager

### UI Module

The UI module implements the user interface:

- `app.py`: Implements the main application window and UI components

### Plugin Module

The plugin module provides integration with 3ds Max:

- `max_integration.py`: Implements the 3ds Max plugin

## Development Environment Setup

### Prerequisites

- Python 3.9-3.11
- Git
- Poetry (optional, for dependency management)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/assethub.git
   cd assethub
   ```

2. Install dependencies:
   ```bash
   # Using pip
   pip install -e .
   
   # Or using Poetry
   poetry install
   ```

3. Run tests:
   ```bash
   python -m unittest discover -s assethub/tests
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Extending AssetHub

### Adding a New Provider

To add a new provider for an external library:

1. Create a new file in `assethub/integration/providers/` (e.g., `sketchfab.py`)
2. Implement the `BaseProvider` interface
3. Register the provider in `assethub/integration/__init__.py`

Example:

```python
from assethub.integration.providers.base import BaseProvider

class SketchfabProvider(BaseProvider):
    """Provider for Sketchfab 3D model library."""
    
    def __init__(self, api_key=None):
        """Initialize the Sketchfab provider."""
        # Implementation
        
    def connect(self):
        """Connect to Sketchfab API."""
        # Implementation
        
    def search(self, query, asset_type=None, page=1, page_size=20):
        """Search for assets in Sketchfab."""
        # Implementation
        
    def get_asset_details(self, asset_id):
        """Get detailed information about an asset."""
        # Implementation
        
    def download_asset(self, asset_id, destination_path):
        """Download an asset from Sketchfab."""
        # Implementation
        
    def get_preview(self, asset_id, destination_path):
        """Download a preview image for an asset."""
        # Implementation
```

Then register the provider in `assethub/integration/__init__.py`:

```python
from assethub.integration.providers.sketchfab import SketchfabProvider

# In the _register_providers method
self.register_provider("sketchfab", SketchfabProvider)
```

### Adding a New File Format

To add support for a new file format:

1. Update the file type detection in `assethub/catalog/scanner.py`
2. Add metadata extraction for the new format if needed

Example:

```python
# In the _get_file_type method in scanner.py
elif ext.lower() in ['.gltf', '.glb']:
    return 'model', 'gltf'
```

### Extending the UI

To add new UI components:

1. Modify `assethub/ui/app.py` to add new widgets or functionality
2. Ensure proper signal/slot connections for event handling

### Extending the 3ds Max Plugin

To extend the 3ds Max plugin:

1. Modify `assethub/plugin/max_integration.py` to add new functionality
2. Test the plugin in 3ds Max to ensure compatibility

## API Reference

### Core Module

#### Config

```python
class Config:
    """Configuration manager for AssetHub."""
    
    def __init__(self, config_path=None):
        """Initialize the configuration manager."""
        
    def get(self, section, key, default=None):
        """Get a configuration value."""
        
    def set(self, section, key, value):
        """Set a configuration value."""
        
    def save_config(self):
        """Save the configuration to disk."""
        
    def load_config(self):
        """Load the configuration from disk."""
        
    def get_storage_path(self):
        """Get the storage path for assets."""
        
    def get_index_path(self):
        """Get the path for the search index."""
```

#### Models

```python
def init_db(db_path=None):
    """Initialize the database."""
    
def get_session():
    """Get a database session."""
    
class Asset(Base):
    """Asset model."""
    
class Tag(Base):
    """Tag model."""
    
class Category(Base):
    """Category model."""
    
class SearchIndex(Base):
    """Search index model."""
```

### Catalog Module

#### Scanner

```python
class AssetScanner:
    """Scanner for asset files."""
    
    def __init__(self):
        """Initialize the asset scanner."""
        
    def scan_directory(self, directory, recursive=True):
        """Scan a directory for assets."""
        
    def scan_file(self, file_path):
        """Scan a single file."""
```

#### Indexer

```python
class AssetIndexer:
    """Indexer for 3D assets."""
    
    def __init__(self):
        """Initialize the asset indexer."""
        
    def create_index(self):
        """Create a new search index."""
        
    def rebuild_index(self):
        """Rebuild the search index from scratch."""
        
    def index_assets(self, assets):
        """Index a list of assets."""
        
    def remove_asset(self, asset_id):
        """Remove an asset from the index."""
```

#### Search

```python
class AssetSearch:
    """Search engine for 3D assets."""
    
    def __init__(self):
        """Initialize the asset search engine."""
        
    def search(self, query_string, fields=None, filters=None, limit=50):
        """Search for assets matching the query."""
        
    def get_asset_by_id(self, asset_id):
        """Get an asset by ID."""
        
    def get_tags(self):
        """Get all unique tags in the index."""
        
    def get_categories(self):
        """Get all unique categories in the index."""
        
    def get_file_types(self):
        """Get all unique file types in the index."""
        
    def get_file_formats(self):
        """Get all unique file formats in the index."""
```

### Integration Module

#### BaseProvider

```python
class BaseProvider(abc.ABC):
    """Base class for external asset library providers."""
    
    @abc.abstractmethod
    def connect(self):
        """Connect to the external library."""
        
    @abc.abstractmethod
    def search(self, query, asset_type=None, page=1, page_size=20):
        """Search for assets in the external library."""
        
    @abc.abstractmethod
    def get_asset_details(self, asset_id):
        """Get detailed information about an asset."""
        
    @abc.abstractmethod
    def download_asset(self, asset_id, destination_path):
        """Download an asset from the external library."""
        
    @abc.abstractmethod
    def get_preview(self, asset_id, destination_path):
        """Download a preview image for an asset."""
```

#### IntegrationManager

```python
class IntegrationManager:
    """Manager for external asset library integrations."""
    
    def __init__(self):
        """Initialize the integration manager."""
        
    def register_provider(self, name, provider_class):
        """Register a provider."""
        
    def get_provider(self, name):
        """Get a provider by name."""
        
    def get_providers(self):
        """Get list of available providers."""
        
    def search_all(self, query, asset_type=None, page=1, page_size=20):
        """Search for assets in all registered providers."""
        
    def download_asset(self, provider_name, asset_id, destination_path):
        """Download an asset from a specific provider."""
        
    def get_asset_details(self, provider_name, asset_id):
        """Get detailed information about an asset."""
        
    def get_preview(self, provider_name, asset_id, destination_path):
        """Download a preview image for an asset."""
```

## Testing

AssetHub uses the unittest framework for testing. Tests are located in the `assethub/tests/` directory.

To run all tests:

```bash
python -m unittest discover -s assethub/tests
```

To run a specific test:

```bash
python -m unittest assethub.tests.test_core
```

## Coding Standards

AssetHub follows PEP 8 coding standards with the following additions:

- Use docstrings for all modules, classes, and functions
- Use type hints for function parameters and return values
- Keep line length to 88 characters or less
- Use meaningful variable and function names
- Write unit tests for all new functionality

## Contributing

We welcome contributions to AssetHub! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for your changes
5. Submit a pull request

Please ensure your code follows our coding standards and passes all tests.

## License

AssetHub is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or support, please contact the AssetHub team at [email@example.com](mailto:email@example.com).
