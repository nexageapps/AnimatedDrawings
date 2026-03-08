"""
SQLAlchemy ORM Models for Themed Animation Platform

Maps domain models to database tables using SQLAlchemy ORM.

Requirements: 9.2
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, 
    Text, JSON, Index, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User ORM model"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_drawings = Column(Integer, default=0)
    
    # Relationships
    drawings = relationship('Drawing', back_populates='user')
    notifications = relationship('Notification', back_populates='user')


class Theme(Base):
    """Theme ORM model"""
    __tablename__ = 'themes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    background_image_url = Column(Text)
    dimensions_width = Column(Integer, nullable=False)
    dimensions_height = Column(Integer, nullable=False)
    max_entities = Column(Integer, default=50)
    positioning_rules = Column(JSON)
    motion_sequences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    themed_worlds = relationship('ThemedWorld', back_populates='theme')
    drawings = relationship('Drawing', back_populates='theme')


class ThemedWorld(Base):
    """Themed World ORM model"""
    __tablename__ = 'themed_worlds'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    theme_id = Column(UUID(as_uuid=True), ForeignKey('themes.id'), nullable=False)
    instance_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    entity_count = Column(Integer, default=0)
    is_full = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    theme = relationship('Theme', back_populates='themed_worlds')
    drawing_entities = relationship('DrawingEntity', back_populates='world')
    
    # Unique constraint
    __table_args__ = (
        Index('idx_themed_worlds_theme_id', 'theme_id'),
        Index('idx_themed_worlds_is_full', 'is_full'),
    )


class Drawing(Base):
    """Drawing ORM model"""
    __tablename__ = 'drawings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    original_image_url = Column(Text, nullable=False)
    normalized_image_url = Column(Text)
    status = Column(String(50), nullable=False)  # pending, processing, animated, failed
    theme_id = Column(UUID(as_uuid=True), ForeignKey('themes.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    user = relationship('User', back_populates='drawings')
    theme = relationship('Theme', back_populates='drawings')
    animation_data = relationship('AnimationData', back_populates='drawing', uselist=False)
    drawing_entities = relationship('DrawingEntity', back_populates='drawing')
    processing_jobs = relationship('ProcessingJob', back_populates='drawing')
    notifications = relationship('Notification', back_populates='drawing')
    
    # Indexes
    __table_args__ = (
        Index('idx_drawings_user_id', 'user_id'),
        Index('idx_drawings_status', 'status'),
        Index('idx_drawings_theme_id', 'theme_id'),
    )


class AnimationData(Base):
    """Animation Data ORM model"""
    __tablename__ = 'animation_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawing_id = Column(UUID(as_uuid=True), ForeignKey('drawings.id'), unique=True, nullable=False)
    character_detected = Column(Boolean, nullable=False)
    segmentation_mask_url = Column(Text)
    skeleton_data = Column(JSON)
    motion_sequence = Column(String(100))
    animation_file_url = Column(Text)
    sprite_sheet_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    drawing = relationship('Drawing', back_populates='animation_data')


class DrawingEntity(Base):
    """Drawing Entity ORM model"""
    __tablename__ = 'drawing_entities'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawing_id = Column(UUID(as_uuid=True), ForeignKey('drawings.id'), nullable=False)
    world_id = Column(UUID(as_uuid=True), ForeignKey('themed_worlds.id'), nullable=False)
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    z_index = Column(Integer, default=0)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    drawing = relationship('Drawing', back_populates='drawing_entities')
    world = relationship('ThemedWorld', back_populates='drawing_entities')
    
    # Indexes
    __table_args__ = (
        Index('idx_drawing_entities_world_id', 'world_id'),
    )


class ProcessingJob(Base):
    """Processing Job ORM model"""
    __tablename__ = 'processing_jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    drawing_id = Column(UUID(as_uuid=True), ForeignKey('drawings.id'), nullable=False)
    job_type = Column(String(50), nullable=False)  # image_processing, animation, composition
    status = Column(String(50), nullable=False)  # queued, processing, completed, failed
    priority = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    drawing = relationship('Drawing', back_populates='processing_jobs')
    
    # Indexes
    __table_args__ = (
        Index('idx_processing_jobs_status', 'status'),
        Index('idx_processing_jobs_drawing_id', 'drawing_id'),
    )


class Notification(Base):
    """Notification ORM model"""
    __tablename__ = 'notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    drawing_id = Column(UUID(as_uuid=True), ForeignKey('drawings.id'))
    notification_type = Column(String(50), nullable=False)  # success, error, acknowledgment
    sent_at = Column(DateTime, default=datetime.utcnow)
    email_content = Column(Text)
    delivery_status = Column(String(50), default='sent')
    
    # Relationships
    user = relationship('User', back_populates='notifications')
    drawing = relationship('Drawing', back_populates='notifications')


class SystemLog(Base):
    """System Log ORM model"""
    __tablename__ = 'system_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)  # info, warning, error, critical
    component = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    log_metadata = Column('metadata', JSON)  # Renamed to avoid reserved word conflict
    created_at = Column(DateTime, default=datetime.utcnow)


# Database engine and session factory
_engine = None
_SessionFactory = None


def init_db(connection_string: str, echo: bool = False, pool_size: int = 10, max_overflow: int = 20):
    """
    Initialize database engine and session factory
    
    Args:
        connection_string: PostgreSQL connection string
        echo: Whether to echo SQL statements (for debugging)
        pool_size: Number of connections to maintain in the pool
        max_overflow: Maximum number of connections to create beyond pool_size
    """
    global _engine, _SessionFactory
    
    _engine = create_engine(
        connection_string,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
    )
    
    _SessionFactory = sessionmaker(bind=_engine)


def get_engine():
    """Get the database engine"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine


def get_session():
    """
    Get a new database session
    
    Returns:
        SQLAlchemy Session instance
        
    Usage:
        session = get_session()
        try:
            # Use session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    """
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionFactory()


def create_all_tables():
    """Create all tables in the database"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    Base.metadata.create_all(_engine)


def drop_all_tables():
    """Drop all tables from the database (use with caution!)"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    Base.metadata.drop_all(_engine)
