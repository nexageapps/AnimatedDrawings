"""
Demo script for World Compositor Service

Demonstrates the spatial positioning algorithm with visual output.
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


def create_demo_theme():
    """Create a demo theme"""
    return Theme(
        id=str(uuid4()),
        name='jungle',
        display_name='Jungle Adventure',
        background_image_url='/static/backgrounds/jungle.jpg',
        dimensions=(1920, 1080),
        max_entities=50,
        positioning_rules={'type': 'ground_based'},
        motion_sequences=['zombie', 'jumping', 'wave_hello']
    )


def create_demo_world(theme_id):
    """Create a demo world"""
    return ThemedWorld(
        id=str(uuid4()),
        theme_id=theme_id,
        instance_number=1,
        entity_count=0,
        is_full=False,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )


def visualize_world(world, theme, entities, title="World Visualization"):
    """
    Create a simple ASCII visualization of the world.
    
    Args:
        world: ThemedWorld instance
        theme: Theme instance
        entities: List of DrawingEntity instances
        title: Title for the visualization
    """
    width, height = theme.dimensions
    
    # Scale down for ASCII display (1 char = 40 pixels)
    scale = 40
    display_width = width // scale
    display_height = height // scale
    
    # Create grid
    grid = [[' ' for _ in range(display_width)] for _ in range(display_height)]
    
    # Mark entities
    for i, entity in enumerate(entities):
        # Scale entity position and size
        x1 = entity.x // scale
        y1 = entity.y // scale
        x2 = (entity.x + entity.width) // scale
        y2 = (entity.y + entity.height) // scale
        
        # Use different characters for different entities
        char = str((i + 1) % 10)
        
        # Fill entity area
        for y in range(max(0, y1), min(display_height, y2 + 1)):
            for x in range(max(0, x1), min(display_width, x2 + 1)):
                grid[y][x] = char
    
    # Print visualization
    print(f"\n{title}")
    print("=" * (display_width + 2))
    print("+" + "-" * display_width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * display_width + "+")
    print(f"World: {width}x{height} pixels (scaled to {display_width}x{display_height} chars)")
    print(f"Entities: {len(entities)}")
    print(f"Scale: 1 char = {scale} pixels")
    print()


def demo_progressive_placement():
    """Demonstrate progressive entity placement"""
    print("\n" + "=" * 70)
    print("DEMO: Progressive Entity Placement")
    print("=" * 70)
    
    service = WorldCompositorService()
    theme = create_demo_theme()
    world = create_demo_world(theme.id)
    
    print(f"\nWorld: {theme.display_name}")
    print(f"Dimensions: {theme.dimensions[0]}x{theme.dimensions[1]} pixels")
    print(f"Minimum spacing: {service.MIN_SPACING} pixels")
    
    entities = []
    entity_sizes = [
        (150, 200, "Large character"),
        (100, 150, "Medium character"),
        (120, 180, "Medium-large character"),
        (80, 120, "Small character"),
        (110, 160, "Medium character"),
    ]
    
    for i, (width, height, description) in enumerate(entity_sizes, 1):
        print(f"\n--- Placing Entity {i}: {description} ({width}x{height}) ---")
        
        # Calculate position
        position = service.calculate_position(
            world, theme, width, height, existing_entities=entities
        )
        
        if position is None:
            print(f"✗ Could not find valid position for entity {i}")
            break
        
        print(f"✓ Found position: {position}")
        
        # Create entity
        entity = DrawingEntity(
            id=str(uuid4()),
            drawing_id=str(uuid4()),
            world_id=world.id,
            position=position,
            z_index=i,
            dimensions=(width, height),
            created_at=datetime.utcnow()
        )
        entities.append(entity)
        
        # Show entity details
        print(f"  Position: ({entity.x}, {entity.y})")
        print(f"  Size: {entity.width}x{entity.height}")
        print(f"  Bounding box: {entity.get_bounding_box()}")
        
        # Check spacing from other entities
        if len(entities) > 1:
            min_distance = float('inf')
            for other in entities[:-1]:
                distance = entity.distance_to(other)
                min_distance = min(min_distance, distance)
            print(f"  Minimum distance to other entities: {min_distance:.1f} pixels")
    
    # Visualize final world
    visualize_world(world, theme, entities, "Final World Layout")
    
    # Print entity summary
    print("Entity Summary:")
    print("-" * 70)
    for i, entity in enumerate(entities, 1):
        print(f"Entity {i}: pos=({entity.x:4d}, {entity.y:4d}), "
              f"size=({entity.width:3d}x{entity.height:3d})")


def demo_collision_detection():
    """Demonstrate collision detection"""
    print("\n" + "=" * 70)
    print("DEMO: Collision Detection")
    print("=" * 70)
    
    service = WorldCompositorService()
    theme = create_demo_theme()
    world = create_demo_world(theme.id)
    
    # Place entity at center
    center_entity = DrawingEntity(
        id=str(uuid4()),
        drawing_id=str(uuid4()),
        world_id=world.id,
        position=(860, 440),  # Roughly centered in 1920x1080
        z_index=0,
        dimensions=(200, 200),
        created_at=datetime.utcnow()
    )
    
    print(f"\nCenter entity:")
    print(f"  Position: ({center_entity.x}, {center_entity.y})")
    print(f"  Size: {center_entity.width}x{center_entity.height}")
    print(f"  Bounding box: {center_entity.get_bounding_box()}")
    print(f"  With {service.MIN_SPACING}px spacing: "
          f"({center_entity.x - service.MIN_SPACING}, "
          f"{center_entity.y - service.MIN_SPACING}) to "
          f"({center_entity.x + center_entity.width + service.MIN_SPACING}, "
          f"{center_entity.y + center_entity.height + service.MIN_SPACING})")
    
    # Test various positions
    test_positions = [
        (870, 450, 50, 50, "Inside center entity"),
        (750, 440, 50, 50, "Too close (left)"),
        (1070, 440, 50, 50, "Too close (right)"),
        (860, 330, 50, 50, "Too close (top)"),
        (860, 650, 50, 50, "Too close (bottom)"),
        (700, 440, 50, 50, "Just far enough (left)"),
        (1120, 440, 50, 50, "Just far enough (right)"),
        (400, 400, 100, 100, "Far away"),
    ]
    
    print(f"\nTesting collision detection:")
    print("-" * 70)
    
    for x, y, w, h, description in test_positions:
        collides = service._check_collision(
            x, y, w, h,
            center_entity.x, center_entity.y,
            center_entity.width, center_entity.height,
            service.MIN_SPACING
        )
        
        status = "COLLIDES" if collides else "OK"
        symbol = "✗" if collides else "✓"
        print(f"{symbol} ({x:4d}, {y:4d}) {w:3d}x{h:3d} - {description:25s} [{status}]")


def demo_position_scoring():
    """Demonstrate position scoring algorithm"""
    print("\n" + "=" * 70)
    print("DEMO: Position Scoring Algorithm")
    print("=" * 70)
    
    service = WorldCompositorService()
    theme = create_demo_theme()
    world = create_demo_world(theme.id)
    
    # Place a few entities
    entities = [
        DrawingEntity(
            id=str(uuid4()),
            drawing_id=str(uuid4()),
            world_id=world.id,
            position=(200, 200),
            z_index=0,
            dimensions=(150, 150),
            created_at=datetime.utcnow()
        ),
        DrawingEntity(
            id=str(uuid4()),
            drawing_id=str(uuid4()),
            world_id=world.id,
            position=(1500, 200),
            z_index=0,
            dimensions=(150, 150),
            created_at=datetime.utcnow()
        ),
    ]
    
    print(f"\nExisting entities:")
    for i, entity in enumerate(entities, 1):
        print(f"  Entity {i}: ({entity.x}, {entity.y}) - {entity.width}x{entity.height}")
    
    # Test scoring at various positions
    test_positions = [
        (300, 200, "Near entity 1"),
        (1400, 200, "Near entity 2"),
        (850, 200, "Between entities (top)"),
        (850, 540, "Center of world"),
        (850, 880, "Between entities (bottom)"),
        (200, 880, "Bottom left"),
        (1500, 880, "Bottom right"),
    ]
    
    print(f"\nPosition scores (higher is better):")
    print("-" * 70)
    
    scores = []
    for x, y, description in test_positions:
        score = service._calculate_position_score(
            x, y, 100, 100, entities,
            theme.dimensions[0], theme.dimensions[1]
        )
        scores.append((score, x, y, description))
        print(f"  ({x:4d}, {y:4d}) - {description:30s}: {score:8.2f}")
    
    # Show best position
    scores.sort(reverse=True)
    best_score, best_x, best_y, best_desc = scores[0]
    print(f"\n✓ Best position: ({best_x}, {best_y}) - {best_desc} (score: {best_score:.2f})")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("WORLD COMPOSITOR SERVICE DEMONSTRATION")
    print("=" * 70)
    
    try:
        demo_progressive_placement()
        demo_collision_detection()
        demo_position_scoring()
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
