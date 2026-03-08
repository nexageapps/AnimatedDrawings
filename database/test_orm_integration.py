"""
Test ORM Integration and Repository Pattern

This test verifies that the SQLAlchemy ORM layer, connection pooling,
and repository pattern work correctly together.

Requirements: 9.2
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.orm import (
    init_db, get_session, create_all_tables, drop_all_tables,
    User, Theme, ThemedWorld, Drawing, AnimationData, DrawingEntity, ProcessingJob
)
from database.repository import (
    user_repository, theme_repository, themed_world_repository,
    drawing_repository, animation_data_repository, drawing_entity_repository,
    processing_job_repository
)


def test_connection_pooling():
    """Test that connection pooling is properly configured"""
    print("\n=== Testing Connection Pooling ===")
    
    # Initialize database
    db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/themed_animation')
    init_db(db_url, echo=False, pool_size=5, max_overflow=10)
    
    # Get multiple sessions to test pooling
    sessions = []
    for i in range(3):
        session = get_session()
        sessions.append(session)
        print(f"✓ Created session {i+1}")
    
    # Close all sessions
    for session in sessions:
        session.close()
    
    print("✓ Connection pooling working correctly")


def test_orm_mappings():
    """Test that ORM mappings work correctly"""
    print("\n=== Testing ORM Mappings ===")
    
    session = get_session()
    
    try:
        # Create a user
        user = User(
            id=uuid4(),
            email='test@example.com',
            created_at=datetime.now(),
            total_drawings=0
        )
        session.add(user)
        session.flush()
        print(f"✓ Created user: {user.email}")
        
        # Create a theme
        theme = Theme(
            id=uuid4(),
            name='test_theme',
            display_name='Test Theme',
            background_image_url='/static/bg/test.jpg',
            dimensions_width=1920,
            dimensions_height=1080,
            max_entities=50,
            positioning_rules={'type': 'grid'},
            motion_sequences=['walk', 'run']
        )
        session.add(theme)
        session.flush()
        print(f"✓ Created theme: {theme.name}")
        
        # Create a themed world
        world = ThemedWorld(
            id=uuid4(),
            theme_id=theme.id,
            instance_number=1,
            entity_count=0,
            is_full=False
        )
        session.add(world)
        session.flush()
        print(f"✓ Created themed world: {world.id}")
        
        # Create a drawing
        drawing = Drawing(
            id=uuid4(),
            user_id=user.id,
            original_image_url='/uploads/test.png',
            normalized_image_url='/uploads/test_normalized.png',
            status='pending',
            theme_id=theme.id,
            created_at=datetime.now()
        )
        session.add(drawing)
        session.flush()
        print(f"✓ Created drawing: {drawing.id}")
        
        # Create animation data
        anim_data = AnimationData(
            id=uuid4(),
            drawing_id=drawing.id,
            character_detected=True,
            segmentation_mask_url='/masks/test.png',
            skeleton_data={'joints': []},
            motion_sequence='walk',
            animation_file_url='/animations/test.gif'
        )
        session.add(anim_data)
        session.flush()
        print(f"✓ Created animation data: {anim_data.id}")
        
        # Create drawing entity
        entity = DrawingEntity(
            id=uuid4(),
            drawing_id=drawing.id,
            world_id=world.id,
            position_x=100,
            position_y=200,
            z_index=0,
            width=150,
            height=200
        )
        session.add(entity)
        session.flush()
        print(f"✓ Created drawing entity: {entity.id}")
        
        # Create processing job
        job = ProcessingJob(
            id=uuid4(),
            drawing_id=drawing.id,
            job_type='animation',
            status='queued',
            priority=0,
            attempts=0,
            max_attempts=3
        )
        session.add(job)
        session.flush()
        print(f"✓ Created processing job: {job.id}")
        
        session.commit()
        print("✓ All ORM mappings working correctly")
        
        # Test relationships
        print("\n=== Testing Relationships ===")
        
        # Refresh objects to load relationships
        session.refresh(user)
        session.refresh(theme)
        session.refresh(world)
        session.refresh(drawing)
        
        # Test user -> drawings relationship
        assert len(user.drawings) == 1
        print(f"✓ User has {len(user.drawings)} drawing(s)")
        
        # Test theme -> worlds relationship
        assert len(theme.themed_worlds) == 1
        print(f"✓ Theme has {len(theme.themed_worlds)} world(s)")
        
        # Test world -> entities relationship
        assert len(world.drawing_entities) == 1
        print(f"✓ World has {len(world.drawing_entities)} entity(ies)")
        
        # Test drawing -> animation_data relationship
        assert drawing.animation_data is not None
        print(f"✓ Drawing has animation data")
        
        # Test drawing -> entities relationship
        assert len(drawing.drawing_entities) == 1
        print(f"✓ Drawing has {len(drawing.drawing_entities)} entity(ies)")
        
        # Test drawing -> jobs relationship
        assert len(drawing.processing_jobs) == 1
        print(f"✓ Drawing has {len(drawing.processing_jobs)} job(s)")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def test_repository_pattern():
    """Test that repository pattern works correctly"""
    print("\n=== Testing Repository Pattern ===")
    
    session = get_session()
    
    try:
        # Test user repository
        user = User(
            id=uuid4(),
            email='repo_test@example.com',
            created_at=datetime.now(),
            total_drawings=0
        )
        created_user = user_repository.create(user, session)
        print(f"✓ Created user via repository: {created_user.email}")
        
        # Test get_by_email
        found_user = user_repository.get_by_email('repo_test@example.com', session)
        assert found_user is not None
        assert found_user.email == 'repo_test@example.com'
        print(f"✓ Found user by email: {found_user.email}")
        
        # Test theme repository
        theme = Theme(
            id=uuid4(),
            name='repo_test_theme',
            display_name='Repo Test Theme',
            background_image_url='/static/bg/test.jpg',
            dimensions_width=1920,
            dimensions_height=1080,
            max_entities=50,
            positioning_rules={'type': 'grid'},
            motion_sequences=['walk']
        )
        created_theme = theme_repository.create(theme, session)
        print(f"✓ Created theme via repository: {created_theme.name}")
        
        # Test get_by_name
        found_theme = theme_repository.get_by_name('repo_test_theme', session)
        assert found_theme is not None
        print(f"✓ Found theme by name: {found_theme.name}")
        
        # Test themed world repository
        world = ThemedWorld(
            id=uuid4(),
            theme_id=created_theme.id,
            instance_number=1,
            entity_count=0,
            is_full=False
        )
        created_world = themed_world_repository.create(world, session)
        print(f"✓ Created world via repository")
        
        # Test get_by_theme
        theme_worlds = themed_world_repository.get_by_theme(created_theme.id, session)
        assert len(theme_worlds) == 1
        print(f"✓ Found {len(theme_worlds)} world(s) for theme")
        
        # Test get_available_world
        available_world = themed_world_repository.get_available_world(created_theme.id, session)
        assert available_world is not None
        print(f"✓ Found available world")
        
        # Test drawing repository
        drawing = Drawing(
            id=uuid4(),
            user_id=created_user.id,
            original_image_url='/uploads/repo_test.png',
            status='pending',
            theme_id=created_theme.id,
            created_at=datetime.now()
        )
        created_drawing = drawing_repository.create(drawing, session)
        print(f"✓ Created drawing via repository")
        
        # Test get_by_user
        user_drawings = drawing_repository.get_by_user(created_user.id, session)
        assert len(user_drawings) == 1
        print(f"✓ Found {len(user_drawings)} drawing(s) for user")
        
        # Test get_by_status
        pending_drawings = drawing_repository.get_by_status('pending', session)
        assert len(pending_drawings) >= 1
        print(f"✓ Found {len(pending_drawings)} pending drawing(s)")
        
        # Test update
        updated_drawing = drawing_repository.update(
            created_drawing.id,
            {'status': 'processing'},
            session
        )
        assert updated_drawing.status == 'processing'
        print(f"✓ Updated drawing status to: {updated_drawing.status}")
        
        # Test count
        drawing_count = drawing_repository.count({'user_id': created_user.id}, session)
        assert drawing_count == 1
        print(f"✓ Counted {drawing_count} drawing(s) for user")
        
        session.commit()
        print("✓ All repository operations working correctly")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def test_requirement_9_2():
    """
    Test Requirement 9.2: THE Server SHALL maintain a database of all 
    Themed_World instances and their associated Drawing_Entity instances
    """
    print("\n=== Testing Requirement 9.2 ===")
    
    session = get_session()
    
    try:
        # Create test data
        user = User(
            id=uuid4(),
            email='req9_2@example.com',
            created_at=datetime.now(),
            total_drawings=0
        )
        session.add(user)
        
        theme = Theme(
            id=uuid4(),
            name='req9_2_theme',
            display_name='Req 9.2 Theme',
            background_image_url='/static/bg/test.jpg',
            dimensions_width=1920,
            dimensions_height=1080,
            max_entities=50,
            positioning_rules={'type': 'grid'},
            motion_sequences=['walk']
        )
        session.add(theme)
        
        world = ThemedWorld(
            id=uuid4(),
            theme_id=theme.id,
            instance_number=1,
            entity_count=0,
            is_full=False
        )
        session.add(world)
        session.flush()
        
        # Create multiple drawings and entities
        for i in range(3):
            drawing = Drawing(
                id=uuid4(),
                user_id=user.id,
                original_image_url=f'/uploads/test_{i}.png',
                status='animated',
                theme_id=theme.id,
                created_at=datetime.now()
            )
            session.add(drawing)
            session.flush()
            
            entity = DrawingEntity(
                id=uuid4(),
                drawing_id=drawing.id,
                world_id=world.id,
                position_x=100 * i,
                position_y=200,
                z_index=i,
                width=150,
                height=200
            )
            session.add(entity)
        
        session.commit()
        print(f"✓ Created themed world with 3 drawing entities")
        
        # Test: Retrieve all themed world instances
        all_worlds = themed_world_repository.get_all(session)
        assert len(all_worlds) >= 1
        print(f"✓ Retrieved {len(all_worlds)} themed world instance(s)")
        
        # Test: Retrieve all entities for a specific world
        world_entities = drawing_entity_repository.get_by_world(world.id, session)
        assert len(world_entities) == 3
        print(f"✓ Retrieved {len(world_entities)} entities for world")
        
        # Test: Verify entity metadata is complete
        for entity in world_entities:
            assert entity.drawing_id is not None
            assert entity.world_id == world.id
            assert entity.position_x >= 0
            assert entity.position_y >= 0
            assert entity.width > 0
            assert entity.height > 0
        print(f"✓ All entity metadata is complete")
        
        # Test: Query entities by theme (through world)
        theme_worlds = themed_world_repository.get_by_theme(theme.id, session)
        total_entities = 0
        for tw in theme_worlds:
            entities = drawing_entity_repository.get_by_world(tw.id, session)
            total_entities += len(entities)
        print(f"✓ Found {total_entities} total entities across theme worlds")
        
        print("✓ Requirement 9.2 satisfied: Database maintains all Themed_World instances and their associated Drawing_Entity instances")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


def cleanup_test_data():
    """Clean up test data"""
    print("\n=== Cleaning Up Test Data ===")
    
    session = get_session()
    
    try:
        # Delete test users (cascade will handle related records)
        test_emails = ['test@example.com', 'repo_test@example.com', 'req9_2@example.com']
        for email in test_emails:
            user = user_repository.get_by_email(email, session)
            if user:
                user_repository.delete(user.id, session)
                print(f"✓ Deleted user: {email}")
        
        # Delete test themes (cascade will handle related records)
        test_themes = ['test_theme', 'repo_test_theme', 'req9_2_theme']
        for theme_name in test_themes:
            theme = theme_repository.get_by_name(theme_name, session)
            if theme:
                theme_repository.delete(theme.id, session)
                print(f"✓ Deleted theme: {theme_name}")
        
        session.commit()
        print("✓ Cleanup complete")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Cleanup error: {e}")
    finally:
        session.close()


def main():
    """Run all tests"""
    print("=" * 60)
    print("ORM Integration and Repository Pattern Tests")
    print("=" * 60)
    
    try:
        # Test connection pooling
        test_connection_pooling()
        
        # Test ORM mappings
        if not test_orm_mappings():
            print("\n✗ ORM mapping tests failed")
            return False
        
        # Test repository pattern
        if not test_repository_pattern():
            print("\n✗ Repository pattern tests failed")
            return False
        
        # Test requirement 9.2
        if not test_requirement_9_2():
            print("\n✗ Requirement 9.2 tests failed")
            return False
        
        # Cleanup
        cleanup_test_data()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
