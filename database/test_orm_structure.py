"""
Unit tests for ORM structure validation

Tests ORM model definitions, relationships, and repository interfaces
without requiring a database connection.

Requirements: 9.2
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.orm import (
    User, Theme, ThemedWorld, Drawing, AnimationData,
    DrawingEntity, ProcessingJob, Notification, SystemLog, Base
)
from database.repository import (
    BaseRepository, UserRepository, ThemeRepository, ThemedWorldRepository,
    DrawingRepository, AnimationDataRepository, DrawingEntityRepository,
    ProcessingJobRepository, NotificationRepository, SystemLogRepository
)
from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty


def test_orm_models_defined():
    """Test that all ORM models are properly defined"""
    print("\n=== Testing ORM Model Definitions ===")
    
    models = [
        User, Theme, ThemedWorld, Drawing, AnimationData,
        DrawingEntity, ProcessingJob, Notification, SystemLog
    ]
    
    for model in models:
        assert hasattr(model, '__tablename__'), f"{model.__name__} missing __tablename__"
        assert hasattr(model, '__table__'), f"{model.__name__} missing __table__"
        print(f"✓ {model.__name__} model defined with table '{model.__tablename__}'")
    
    print("✓ All ORM models properly defined")


def test_orm_columns():
    """Test that ORM models have required columns"""
    print("\n=== Testing ORM Columns ===")
    
    # Test User columns
    user_cols = [c.name for c in User.__table__.columns]
    assert 'id' in user_cols
    assert 'email' in user_cols
    assert 'created_at' in user_cols
    assert 'total_drawings' in user_cols
    print(f"✓ User has columns: {user_cols}")
    
    # Test Theme columns
    theme_cols = [c.name for c in Theme.__table__.columns]
    assert 'id' in theme_cols
    assert 'name' in theme_cols
    assert 'display_name' in theme_cols
    assert 'dimensions_width' in theme_cols
    assert 'dimensions_height' in theme_cols
    assert 'max_entities' in theme_cols
    assert 'positioning_rules' in theme_cols
    assert 'motion_sequences' in theme_cols
    print(f"✓ Theme has columns: {theme_cols}")
    
    # Test ThemedWorld columns
    world_cols = [c.name for c in ThemedWorld.__table__.columns]
    assert 'id' in world_cols
    assert 'theme_id' in world_cols
    assert 'instance_number' in world_cols
    assert 'entity_count' in world_cols
    assert 'is_full' in world_cols
    assert 'last_updated' in world_cols
    print(f"✓ ThemedWorld has columns: {world_cols}")
    
    # Test Drawing columns
    drawing_cols = [c.name for c in Drawing.__table__.columns]
    assert 'id' in drawing_cols
    assert 'user_id' in drawing_cols
    assert 'original_image_url' in drawing_cols
    assert 'status' in drawing_cols
    assert 'theme_id' in drawing_cols
    print(f"✓ Drawing has columns: {drawing_cols}")
    
    # Test DrawingEntity columns (Requirement 9.2)
    entity_cols = [c.name for c in DrawingEntity.__table__.columns]
    assert 'id' in entity_cols
    assert 'drawing_id' in entity_cols
    assert 'world_id' in entity_cols
    assert 'position_x' in entity_cols
    assert 'position_y' in entity_cols
    assert 'z_index' in entity_cols
    assert 'width' in entity_cols
    assert 'height' in entity_cols
    print(f"✓ DrawingEntity has columns: {entity_cols}")
    
    print("✓ All required columns present")


def test_orm_relationships():
    """Test that ORM relationships are properly defined"""
    print("\n=== Testing ORM Relationships ===")
    
    # Get mapper for each model
    user_mapper = inspect(User)
    theme_mapper = inspect(Theme)
    world_mapper = inspect(ThemedWorld)
    drawing_mapper = inspect(Drawing)
    
    # Test User relationships
    user_rels = [r.key for r in user_mapper.relationships]
    assert 'drawings' in user_rels
    assert 'notifications' in user_rels
    print(f"✓ User has relationships: {user_rels}")
    
    # Test Theme relationships
    theme_rels = [r.key for r in theme_mapper.relationships]
    assert 'themed_worlds' in theme_rels
    assert 'drawings' in theme_rels
    print(f"✓ Theme has relationships: {theme_rels}")
    
    # Test ThemedWorld relationships (Requirement 9.2)
    world_rels = [r.key for r in world_mapper.relationships]
    assert 'theme' in world_rels
    assert 'drawing_entities' in world_rels
    print(f"✓ ThemedWorld has relationships: {world_rels}")
    
    # Test Drawing relationships
    drawing_rels = [r.key for r in drawing_mapper.relationships]
    assert 'user' in drawing_rels
    assert 'theme' in drawing_rels
    assert 'animation_data' in drawing_rels
    assert 'drawing_entities' in drawing_rels
    assert 'processing_jobs' in drawing_rels
    print(f"✓ Drawing has relationships: {drawing_rels}")
    
    print("✓ All relationships properly defined")


def test_foreign_keys():
    """Test that foreign key constraints are properly defined"""
    print("\n=== Testing Foreign Keys ===")
    
    # Test ThemedWorld foreign keys
    world_fks = [fk.column.table.name for fk in ThemedWorld.__table__.foreign_keys]
    assert 'themes' in world_fks
    print(f"✓ ThemedWorld references: {world_fks}")
    
    # Test Drawing foreign keys
    drawing_fks = [fk.column.table.name for fk in Drawing.__table__.foreign_keys]
    assert 'users' in drawing_fks
    assert 'themes' in drawing_fks
    print(f"✓ Drawing references: {drawing_fks}")
    
    # Test DrawingEntity foreign keys (Requirement 9.2)
    entity_fks = [fk.column.table.name for fk in DrawingEntity.__table__.foreign_keys]
    assert 'drawings' in entity_fks
    assert 'themed_worlds' in entity_fks
    print(f"✓ DrawingEntity references: {entity_fks}")
    
    # Test AnimationData foreign keys
    anim_fks = [fk.column.table.name for fk in AnimationData.__table__.foreign_keys]
    assert 'drawings' in anim_fks
    print(f"✓ AnimationData references: {anim_fks}")
    
    # Test ProcessingJob foreign keys
    job_fks = [fk.column.table.name for fk in ProcessingJob.__table__.foreign_keys]
    assert 'drawings' in job_fks
    print(f"✓ ProcessingJob references: {job_fks}")
    
    print("✓ All foreign keys properly defined")


def test_indexes():
    """Test that performance indexes are defined"""
    print("\n=== Testing Indexes ===")
    
    # Test ThemedWorld indexes
    world_indexes = [idx.name for idx in ThemedWorld.__table__.indexes]
    assert 'idx_themed_worlds_theme_id' in world_indexes
    assert 'idx_themed_worlds_is_full' in world_indexes
    print(f"✓ ThemedWorld has indexes: {world_indexes}")
    
    # Test Drawing indexes
    drawing_indexes = [idx.name for idx in Drawing.__table__.indexes]
    assert 'idx_drawings_user_id' in drawing_indexes
    assert 'idx_drawings_status' in drawing_indexes
    assert 'idx_drawings_theme_id' in drawing_indexes
    print(f"✓ Drawing has indexes: {drawing_indexes}")
    
    # Test DrawingEntity indexes
    entity_indexes = [idx.name for idx in DrawingEntity.__table__.indexes]
    assert 'idx_drawing_entities_world_id' in entity_indexes
    print(f"✓ DrawingEntity has indexes: {entity_indexes}")
    
    # Test ProcessingJob indexes
    job_indexes = [idx.name for idx in ProcessingJob.__table__.indexes]
    assert 'idx_processing_jobs_status' in job_indexes
    assert 'idx_processing_jobs_drawing_id' in job_indexes
    print(f"✓ ProcessingJob has indexes: {job_indexes}")
    
    print("✓ All performance indexes defined")


def test_repository_interfaces():
    """Test that repository classes have required methods"""
    print("\n=== Testing Repository Interfaces ===")
    
    # Test BaseRepository methods
    base_methods = ['create', 'get_by_id', 'get_all', 'find_by', 'find_one_by', 
                    'update', 'delete', 'count']
    for method in base_methods:
        assert hasattr(BaseRepository, method), f"BaseRepository missing {method}"
    print(f"✓ BaseRepository has methods: {base_methods}")
    
    # Test UserRepository
    assert hasattr(UserRepository, 'get_by_email')
    assert hasattr(UserRepository, 'increment_drawing_count')
    print("✓ UserRepository has specialized methods")
    
    # Test ThemeRepository
    assert hasattr(ThemeRepository, 'get_by_name')
    print("✓ ThemeRepository has specialized methods")
    
    # Test ThemedWorldRepository (Requirement 9.2)
    assert hasattr(ThemedWorldRepository, 'get_by_theme')
    assert hasattr(ThemedWorldRepository, 'get_available_world')
    assert hasattr(ThemedWorldRepository, 'increment_entity_count')
    print("✓ ThemedWorldRepository has specialized methods")
    
    # Test DrawingRepository
    assert hasattr(DrawingRepository, 'get_by_user')
    assert hasattr(DrawingRepository, 'get_by_theme')
    assert hasattr(DrawingRepository, 'get_by_status')
    print("✓ DrawingRepository has specialized methods")
    
    # Test DrawingEntityRepository (Requirement 9.2)
    assert hasattr(DrawingEntityRepository, 'get_by_world')
    assert hasattr(DrawingEntityRepository, 'get_by_drawing')
    print("✓ DrawingEntityRepository has specialized methods")
    
    # Test ProcessingJobRepository
    assert hasattr(ProcessingJobRepository, 'get_by_status')
    assert hasattr(ProcessingJobRepository, 'get_by_drawing')
    assert hasattr(ProcessingJobRepository, 'get_queued_jobs')
    print("✓ ProcessingJobRepository has specialized methods")
    
    print("✓ All repository interfaces complete")


def test_requirement_9_2_support():
    """
    Test that ORM structure supports Requirement 9.2:
    THE Server SHALL maintain a database of all Themed_World instances 
    and their associated Drawing_Entity instances
    """
    print("\n=== Testing Requirement 9.2 Support ===")
    
    # Verify ThemedWorld model exists
    assert ThemedWorld is not None
    print("✓ ThemedWorld model exists")
    
    # Verify DrawingEntity model exists
    assert DrawingEntity is not None
    print("✓ DrawingEntity model exists")
    
    # Verify relationship from ThemedWorld to DrawingEntity
    world_mapper = inspect(ThemedWorld)
    world_rels = {r.key: r for r in world_mapper.relationships}
    assert 'drawing_entities' in world_rels
    print("✓ ThemedWorld has 'drawing_entities' relationship")
    
    # Verify relationship from DrawingEntity to ThemedWorld
    entity_mapper = inspect(DrawingEntity)
    entity_rels = {r.key: r for r in entity_mapper.relationships}
    assert 'world' in entity_rels
    print("✓ DrawingEntity has 'world' relationship")
    
    # Verify foreign key from DrawingEntity to ThemedWorld
    entity_fks = {fk.parent.name: fk.column.table.name 
                  for fk in DrawingEntity.__table__.foreign_keys}
    assert 'world_id' in entity_fks
    assert entity_fks['world_id'] == 'themed_worlds'
    print("✓ DrawingEntity has foreign key to ThemedWorld")
    
    # Verify repository methods for querying
    assert hasattr(ThemedWorldRepository, 'get_by_theme')
    assert hasattr(ThemedWorldRepository, 'get_all')
    assert hasattr(DrawingEntityRepository, 'get_by_world')
    print("✓ Repository methods support querying worlds and entities")
    
    # Verify indexes for performance
    entity_indexes = [idx.name for idx in DrawingEntity.__table__.indexes]
    assert 'idx_drawing_entities_world_id' in entity_indexes
    print("✓ Performance index exists for querying entities by world")
    
    print("✓ Requirement 9.2 fully supported by ORM structure")


def main():
    """Run all tests"""
    print("=" * 60)
    print("ORM Structure Validation Tests")
    print("=" * 60)
    
    try:
        test_orm_models_defined()
        test_orm_columns()
        test_orm_relationships()
        test_foreign_keys()
        test_indexes()
        test_repository_interfaces()
        test_requirement_9_2_support()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nORM layer is properly configured with:")
        print("  • SQLAlchemy ORM mappings for all domain models")
        print("  • Bidirectional relationships between entities")
        print("  • Foreign key constraints for data integrity")
        print("  • Performance indexes for common queries")
        print("  • Repository pattern for data access abstraction")
        print("  • Full support for Requirement 9.2")
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
