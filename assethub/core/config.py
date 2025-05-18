"""
Configuration module for AssetHub.

This module provides configuration settings and utilities for the AssetHub application.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for AssetHub."""

    DEFAULT_CONFIG = {
        "database": {
            "type": "sqlite",
            "path": "~/.assethub/database.db"
        },
        "storage": {
            "local_path": "~/.assethub/assets",
            "max_cache_size_gb": 10
        },
        "search": {
            "index_path": "~/.assethub/index",
            "auto_index": True,
            "index_interval_minutes": 60
        },
        "ui": {
            "theme": "light",
            "language": "en"
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        self.config_path = config_path or os.path.expanduser("~/.assethub/config.json")
        self.config_dir = os.path.dirname(self.config_path)
        self._config = self.DEFAULT_CONFIG.copy()
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self._update_config_recursive(self._config, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
        else:
            self._ensure_config_dir()
            self.save_config()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Create other necessary directories
        os.makedirs(self.get_db_path().parent, exist_ok=True)
        os.makedirs(self.get_storage_path(), exist_ok=True)
        os.makedirs(self.get_index_path(), exist_ok=True)

    def _update_config_recursive(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Update configuration recursively.

        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_config_recursive(target[key], value)
            else:
                target[key] = value

    def save_config(self) -> None:
        """Save configuration to file."""
        self._ensure_config_dir()
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        try:
            return self._config[section][key]
        except KeyError:
            return default

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self.save_config()

    def get_db_path(self) -> Path:
        """
        Get database path.

        Returns:
            Path to database file
        """
        db_path = self.get("database", "path")
        return Path(os.path.expanduser(db_path))

    def get_storage_path(self) -> Path:
        """
        Get storage path.

        Returns:
            Path to local storage directory
        """
        storage_path = self.get("storage", "local_path")
        return Path(os.path.expanduser(storage_path))

    def get_index_path(self) -> Path:
        """
        Get search index path.

        Returns:
            Path to search index directory
        """
        index_path = self.get("search", "index_path")
        return Path(os.path.expanduser(index_path))


# Global configuration instance
config = Config()
