"""
Test script for World Compositor Service

Tests the spatial positioning algorithm, collision detection, and placement logic.
"""

import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.world_compositor_service import WorldCompositorService
from models.themed_world import ThemedWorld
from models.drawing_entity import DrawingEntity
from models.theme import Theme


def create_test_theme(width=1920, height=1080):
    """Create a test theme for testing"""
    return Theme(
        id=str(uuid4()),
        name='test_theme',
        display_name='Test Theme',
        background_image_url='',
        dimensions=(width, height),
        max_entities=50,
        positioning_rules={},
        motion_sequences=['wave_hello']
    )


def create_test_world(theme_id):
    """Create a test world for testing"""
    return ThemedWorld(
        id=str(uuid4()),
        theme_id=theme_id,
        instance_number=1,
        entity_count=0,
        is_full=False,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )


def create_test_entity(world_id, x, y, width, height):
    """Create a test entity for testing"""
    return DrawingEntity(
        id=str(uuid4()),
        drawing_id=str(uuid4()),
        world_id=world_id,
        position=(x, y),
        z_index=0,
        dimensions=(width, height),
        created_at=datetime.utcnow()
    )


def test_minimum_spacing_enforcement():
    """Test that minimum spacing of 50 pixels is enforced"""
    print("\nTest: Minimum Spacing Enforcement (50 pixels)")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme()
    world = create_test_world(theme.id)
    
    # Place first entity at (100, 100) with size 100x100
    entity1 = create_test_entity(world.id, 100, 100, 100, 100)
    existing_entities = [entity1]
    
    # Try to place second entity too close (should fail validation)
    # Entity1 occupies (100, 100) to (200, 200)
    # With 50px spacing, no entity should be placed within (50, 50) to (250, 250)
    
    # Test collision detection directly
    print(f"Entity 1: position=({entity1.x}, {entity1.y}), size=({entity1.width}x{entity1.height})")
    print(f"Entity 1 bounding box with spacing: (50, 50) to (250, 250)")
    
    # Position too close (should collide)
    collides = service._check_collision(
        120, 120, 50, 50,  # New entity at (120, 120), size 50x50
        entity1.x, entity1.y, entity1.width, entity1.height,
        service.MIN_SPACING
    )
    print(f"\nPosition (120, 120) with size 50x50: {'COLLIDES ✓' if collides else 'NO COLLISION ✗'}")
    assert collides, "Should detect collision when entities are too close"
    
    # Position far enough (should not collide)
    collides = service._check_collision(
        300, 300, 50, 50,  # New entity at (300, 300), size 50x50
        entity1.x, entity1.y, entity1.width, entity1.height,
        service.MIN_SPACING
    )
    print(f"Position (300, 300) with size 50x50: {'COLLIDES ✗' if collides else 'NO COLLISION ✓'}")
    assert not collides, "Should not detect collision when entities are far enough"
    
    print("\n✓ Minimum spacing enforcement works correctly")


def test_position_validation():
    """Test position validation (bounds checking and collision detection)"""
    print("\nTest: Position Validation")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme(width=800, height=600)
    world = create_test_world(theme.id)
    
    # Test bounds checking
    print("Testing bounds checking...")
    
    # Valid position
    valid = service._is_position_valid(100, 100, 50, 50, [], 800, 600)
    print(f"Position (100, 100) with size 50x50 in 800x600 world: {'VALID ✓' if valid else 'INVALID ✗'}")
    assert valid, "Should be valid position"
    
    # Out of bounds (x)
    valid = service._is_position_valid(760, 100, 50, 50, [], 800, 600)
    print(f"Position (760, 100) with size 50x50 in 800x600 world: {'VALID ✗' if valid else 'INVALID ✓'}")
    assert not valid, "Should be invalid (exceeds width)"
    
    # Out of bounds (y)
    valid = service._is_position_valid(100, 560, 50, 50, [], 800, 600)
    print(f"Position (100, 560) with size 50x50 in 800x600 world: {'VALID ✗' if valid else 'INVALID ✓'}")
    assert not valid, "Should be invalid (exceeds height)"
    
    # Negative position
    valid = service._is_position_valid(-10, 100, 50, 50, [], 800, 600)
    print(f"Position (-10, 100) with size 50x50 in 800x600 world: {'VALID ✗' if valid else 'INVALID ✓'}")
    assert not valid, "Should be invalid (negative x)"
    
    print("\n✓ Position validation works correctly")


def test_calculate_position_empty_world():
    """Test position calculation in an empty world"""
    print("\nTest: Calculate Position in Empty World")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme()
    world = create_test_world(theme.id)
    
    # Calculate position for first entity
    position = service.calculate_position(
        world, theme, 100, 100, existing_entities=[]
    )
    
    print(f"World dimensions: {theme.dimensions}")
    print(f"Entity size: 100x100")
    print(f"Calculated position: {position}")
    
    assert position is not None, "Should find a valid position"
    x, y = position
    assert 0 <= x <= theme.dimensions[0] - 100, "X coordinate should be within bounds"
    assert 0 <= y <= theme.dimensions[1] - 100, "Y coordinate should be within bounds"
    
    print("✓ Position calculation works for empty world")


def test_calculate_position_with_existing_entities():
    """Test position calculation with existing entities"""
    print("\nTest: Calculate Position with Existing Entities")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme()
    world = create_test_world(theme.id)
    
    # Place some entities
    entity1 = create_test_entity(world.id, 100, 100, 150, 150)
    entity2 = create_test_entity(world.id, 400, 400, 100, 100)
    existing_entities = [entity1, entity2]
    
    print(f"Existing entities:")
    print(f"  Entity 1: position=({entity1.x}, {entity1.y}), size=({entity1.width}x{entity1.height})")
    print(f"  Entity 2: position=({entity2.x}, {entity2.y}), size=({entity2.width}x{entity2.height})")
    
    # Calculate position for new entity
    position = service.calculate_position(
        world, theme, 80, 80, existing_entities=existing_entities
    )
    
    print(f"\nNew entity size: 80x80")
    print(f"Calculated position: {position}")
    
    assert position is not None, "Should find a valid position"
    
    # Verify no collision with existing entities
    new_entity = create_test_entity(world.id, position[0], position[1], 80, 80)
    
    for i, entity in enumerate(existing_entities, 1):
        collides = new_entity.overlaps_with(entity, service.MIN_SPACING)
        print(f"Collision with entity {i}: {'YES ✗' if collides else 'NO ✓'}")
        assert not collides, f"Should not collide with entity {i}"
    
    print("\n✓ Position calculation respects existing entities")


def test_position_scoring():
    """Test position scoring algorithm"""
    print("\nTest: Position Scoring Algorithm")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme()
    world = create_test_world(theme.id)
    
    # Place one entity
    entity1 = create_test_entity(world.id, 100, 100, 100, 100)
    existing_entities = [entity1]
    
    print(f"Existing entity: position=({entity1.x}, {entity1.y}), size=({entity1.width}x{entity1.height})")
    
    # Calculate scores for different positions
    positions_to_test = [
        (150, 150, "Very close to existing entity"),
        (300, 300, "Moderate distance from existing entity"),
        (800, 800, "Far from existing entity"),
    ]
    
    print("\nPosition scores:")
    for x, y, description in positions_to_test:
        score = service._calculate_position_score(
            x, y, 80, 80, existing_entities, theme.dimensions[0], theme.dimensions[1]
        )
        print(f"  ({x}, {y}) - {description}: {score:.2f}")
    
    # Verify that farther positions generally score higher
    score_close = service._calculate_position_score(
        150, 150, 80, 80, existing_entities, theme.dimensions[0], theme.dimensions[1]
    )
    score_far = service._calculate_position_score(
        800, 800, 80, 80, existing_entities, theme.dimensions[0], theme.dimensions[1]
    )
    
    print(f"\nScore comparison:")
    print(f"  Close position (150, 150): {score_close:.2f}")
    print(f"  Far position (800, 800): {score_far:.2f}")
    print(f"  Far position scores {'higher ✓' if score_far > score_close else 'lower ✗'}")
    
    assert score_far > score_close, "Farther positions should generally score higher"
    
    print("\n✓ Position scoring algorithm works correctly")


def test_grid_based_collision_detection():
    """Test grid-based collision detection"""
    print("\nTest: Grid-Based Collision Detection")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme()
    world = create_test_world(theme.id)
    
    # Create a grid of entities
    entities = []
    for i in range(3):
        for j in range(3):
            x = 100 + i * 300
            y = 100 + j * 300
            entity = create_test_entity(world.id, x, y, 100, 100)
            entities.append(entity)
    
    print(f"Created {len(entities)} entities in a 3x3 grid")
    
    # Build occupancy grid
    grid = service._build_occupancy_grid(
        entities, theme.dimensions[0], theme.dimensions[1], service.GRID_STEP
    )
    
    print(f"Occupancy grid has {len(grid)} occupied cells")
    print(f"Grid step size: {service.GRID_STEP} pixels")
    
    assert len(grid) > 0, "Grid should have occupied cells"
    
    print("\n✓ Grid-based collision detection works")


def test_entity_too_large():
    """Test handling of entity that's too large for the world"""
    print("\nTest: Entity Too Large for World")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme(width=500, height=500)
    world = create_test_world(theme.id)
    
    print(f"World dimensions: {theme.dimensions}")
    print(f"Entity size: 600x600 (too large)")
    
    # Try to place entity larger than world
    position = service.calculate_position(
        world, theme, 600, 600, existing_entities=[]
    )
    
    print(f"Calculated position: {position}")
    assert position is None, "Should return None for entity too large"
    
    print("✓ Correctly handles entity too large for world")


def test_world_at_capacity():
    """Test behavior when world is nearly full"""
    print("\nTest: World at Capacity")
    print("=" * 60)
    
    service = WorldCompositorService()
    theme = create_test_theme(width=800, height=600)
    world = create_test_world(theme.id)
    
    # Fill world with many entities
    entities = []
    entity_size = 80
    spacing = entity_size + service.MIN_SPACING
    
    count = 0
    for x in range(0, 800 - entity_size, spacing):
        for y in range(0, 600 - entity_size, spacing):
            entity = create_test_entity(world.id, x, y, entity_size, entity_size)
            entities.append(entity)
            count += 1
    
    print(f"Placed {count} entities in world")
    print(f"World dimensions: {theme.dimensions}")
    print(f"Entity size: {entity_size}x{entity_size}")
    print(f"Minimum spacing: {service.MIN_SPACING} pixels")
    
    # Try to place one more entity
    position = service.calculate_position(
        world, theme, entity_size, entity_size, existing_entities=entities
    )
    
    if position is None:
        print("No valid position found (world is full) ✓")
    else:
        print(f"Found position: {position}")
        # Verify it doesn't collide
        new_entity = create_test_entity(world.id, position[0], position[1], entity_size, entity_size)
        for entity in entities:
            assert not new_entity.overlaps_with(entity, service.MIN_SPACING), "Should not collide"
        print("Found valid position even in crowded world ✓")
    
    print("\n✓ Handles world at capacity correctly")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("WORLD COMPOSITOR SERVICE TESTS")
    print("=" * 60)
    
    try:
        test_minimum_spacing_enforcement()
        test_position_validation()
        test_calculate_position_empty_world()
        test_calculate_position_with_existing_entities()
        test_position_scoring()
        test_grid_based_collision_detection()
        test_entity_too_large()
        test_world_at_capacity()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
