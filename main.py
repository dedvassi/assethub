"""
Main entry point for AssetHub application.

This module provides the entry point for running the AssetHub application.
"""
import sys
import logging
from assethub.ui.app import run_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting AssetHub application")
    run_app()
