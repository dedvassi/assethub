"""
Core models for AssetHub.

This module provides the core data models for the AssetHub application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class Asset:
    """Asset data model."""
    
    id: str
    name: str
    file_path: str
    file_type: str  # model, texture, material, hdri, etc.
    file_format: str  # fbx, obj, png, jpg, etc.
    source: str  # local, Poly Haven, etc.
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    preview_path: Optional[str] = None
    date_added: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)


@dataclass
class Category:
    """Category data model."""
    
    id: str
    name: str
    parent_id: Optional[str] = None
    subcategories: List[str] = field(default_factory=list)


@dataclass
class SearchIndex:
    """Search index data model."""
    
    assets: Dict[str, Asset] = field(default_factory=dict)
    categories: Dict[str, Category] = field(default_factory=dict)
    tags: Dict[str, List[str]] = field(default_factory=dict)
