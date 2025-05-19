"""
Configuration module for AssetHub.

This module provides configuration settings for the AssetHub application.
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "app_name": "AssetHub",
    "version": "1.0.0",
    "data_dir": str(Path.home() / ".assethub"),
    "index_file": "index.json",
    "preview_dir": "previews",
    "cache_dir": "cache",
    "max_preview_size": 512,
    "supported_formats": {
        "model": ["fbx", "obj", "blend", "max", "c4d", "ma", "mb"],
        "texture": ["png", "jpg", "jpeg", "tif", "tiff", "exr", "hdr"],
        "material": ["mtl", "mat", "sbsar"],
        "hdri": ["hdr", "exr"]
    },
    "providers": ["local", "Poly Haven", "Free3D"]
}

# Global config object
config = {}


def load_config():
    """Load configuration from file or create default."""
    global config
    
    # Set default config
    config = DEFAULT_CONFIG.copy()
    
    # Create data directory if it doesn't exist
    data_dir = Path(config["data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create preview directory if it doesn't exist
    preview_dir = data_dir / config["preview_dir"]
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    # Create cache directory if it doesn't exist
    cache_dir = data_dir / config["cache_dir"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Load config from file if it exists
    config_file = data_dir / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
    else:
        # Save default config
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=4)
            logger.info(f"Created default configuration at {config_file}")
        except Exception as e:
            logger.error(f"Error saving default configuration: {str(e)}")
    
    return config


def save_config():
    """Save configuration to file."""
    try:
        config_file = Path(config["data_dir"]) / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
        logger.info(f"Saved configuration to {config_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False


def get_data_dir():
    """Get the data directory path."""
    return Path(config["data_dir"])


def get_index_file():
    """Get the index file path."""
    return get_data_dir() / config["index_file"]


def get_preview_dir():
    """Get the preview directory path."""
    return get_data_dir() / config["preview_dir"]


def get_cache_dir():
    """Get the cache directory path."""
    return get_data_dir() / config["cache_dir"]


# Load configuration on module import
load_config()
