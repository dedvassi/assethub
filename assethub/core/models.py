"""
Data models for AssetHub.

This module defines the database models used in the AssetHub application.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from assethub.core.config import config

Base = declarative_base()

# Association table for many-to-many relationship between assets and tags
asset_tags = Table(
    'asset_tags',
    Base.metadata,
    Column('asset_id', Integer, ForeignKey('assets.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Association table for many-to-many relationship between assets and categories
asset_categories = Table(
    'asset_categories',
    Base.metadata,
    Column('asset_id', Integer, ForeignKey('assets.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class Asset(Base):
    """Model representing a 3D asset (model, texture, material)."""
    
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # e.g., "model", "texture", "material"
    file_format = Column(String(20), nullable=False)  # e.g., "obj", "fbx", "jpg", "png"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    
    # Source information
    source = Column(String(255), nullable=True)  # e.g., "local", "turbosquid", "cgtrader"
    source_url = Column(String(1024), nullable=True)
    source_id = Column(String(255), nullable=True)
    
    # Preview
    preview_path = Column(String(1024), nullable=True)
    
    # Relationships
    tags = relationship("Tag", secondary=asset_tags, back_populates="assets")
    categories = relationship("Category", secondary=asset_categories, back_populates="assets")
    
    # Model-specific properties (for 3D models)
    vertex_count = Column(Integer, nullable=True)
    face_count = Column(Integer, nullable=True)
    material_count = Column(Integer, nullable=True)
    
    # Texture-specific properties
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    
    # Additional properties stored as JSON
    properties = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', type='{self.file_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert asset to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "file_format": self.file_format,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count,
            "source": self.source,
            "source_url": self.source_url,
            "source_id": self.source_id,
            "preview_path": self.preview_path,
            "tags": [tag.name for tag in self.tags],
            "categories": [category.name for category in self.categories],
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
            "material_count": self.material_count,
            "width": self.width,
            "height": self.height,
            "channels": self.channels,
            "properties": self.properties
        }


class Tag(Base):
    """Model representing a tag for assets."""
    
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    assets = relationship("Asset", secondary=asset_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Category(Base):
    """Model representing a category for assets."""
    
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    assets = relationship("Asset", secondary=asset_categories, back_populates="categories")
    children = relationship("Category", backref=relationship("Category", remote_side=[id]))
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class SearchIndex(Base):
    """Model representing search index metadata."""
    
    __tablename__ = 'search_indices'
    
    id = Column(Integer, primary_key=True)
    path = Column(String(1024), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    document_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<SearchIndex(id={self.id}, path='{self.path}')>"


def init_db():
    """Initialize the database."""
    db_path = config.get_db_path()
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a database session."""
    engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()
