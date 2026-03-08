"""
Demo script for Theme-Specific Positioning Rules

Demonstrates how different themes position entities according to their
unique positioning strategies.

Requirements: 5.1, 6.5
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


def create_theme(name, width=1920, height=1080):
    """Create a theme"""
    return Theme(
        id=str(uuid4()),
        name=name,
        display_name=name.title(),
        background_image_url=f'/assets/backgrounds/{name}.jpg',
        dimensions=(width, height),
        max_entities=50,
        positioning_rules={},
        motion_sequences=['wave_hello', 'dance', 'walk']
    )


def create_world(theme_id):
    """Create a world"""
    return ThemedWorld(
        id=str(uuid4()),
        theme_id=theme_id,
        instance_number=1,
        entity_count=0,
        is_full=False,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )


def visualize_positions(theme_name, positions, world_width, world_height):
    """
    Create a simple ASCII visualization of entity positions.
    
    Args:
        theme_name: Name of the theme
        positions: List of (x, y, width, height) tuples
        world_width: Width of world
        world_height: Height of world
    """
    # Create a grid (scaled down)
    scale = 40  # Each character represents 40 pixels
    grid_width = world_width // scale
    grid_height = world_height // scale
    
    # Initialize grid
    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Place entities on grid
    for i, (x, y, w, h) in enumerate(positions):
        grid_x = x // scale
        grid_y = y // scale
        grid_w = max(1, w // scale)
        grid_h = max(1, h // scale)
        
        # Mark entity position
        entity_char = str(i + 1) if i < 9 else '*'
        for dy in range(grid_h):
            for dx in range(grid_w):
                gx = grid_x + dx
                gy = grid_y + dy
                if 0 <= gx < grid_width and 0 <= gy < grid_height:
                    grid[gy][gx] = entity_char
    
    # Print grid
    print(f"\n{theme_name.upper()} THEME - Entity Placement Visualization")
    print("=" * (grid_width + 2))
    print("+" + "-" * grid_width + "+")
    for row in grid:
        print("|" + "".join(row) + "|")
    print("+" + "-" * grid_width + "+")
    print(f"World: {world_width}x{world_height} pixels")
    print(f"Scale: 1 character = {scale} pixels")
    print(f"Entities: {len(positions)}")


def demo_theme_positioning(theme_name, num_entities=10):
    """
    Demonstrate positioning for a specific theme.
    
    Args:
        theme_name: Name of the theme to demo
        num_entities: Number of entities to place
    """
    print(f"\n{'=' * 60}")
    print(f"DEMO: {theme_name.upper()} THEME POSITIONING")
    print(f"{'=' * 60}")
    
    # Create theme and world
    theme = create_theme(theme_name)
    world = create_world(theme.id)
    service = WorldCompositorService()
    
    print(f"\nTheme: {theme.display_name}")
    print(f"World dimensions: {theme.dimensions}")
    print(f"Placing {num_entities} entities...")
    
    # Place entities
    entities = []
    positions = []
    
    for i in range(num_entities):
        # Vary entity sizes
        if i % 3 == 0:
            width, height = 150, 200  # Large
        elif i % 3 == 1:
            width, height = 100, 100  # Medium
        else:
            width, height = 60, 80    # Small
        
        # Calculate position
        position = service.calculate_position(
            world, theme, width, height, existing_entities=entities
        )
        
        if position:
            x, y = position
            entity = DrawingEntity(
                id=str(uuid4()),
                drawing_id=str(uuid4()),
                world_id=world.id,
                position=position,
                z_index=0,
                dimensions=(width, height),
                created_at=datetime.utcnow()
            )
            entities.append(entity)
            positions.append((x, y, width, height))
            
            print(f"  Entity {i+1}: size={width}x{height}, position=({x}, {y})")
        else:
            print(f"  Entity {i+1}: Could not find valid position")
    
    # Visualize
    if positions:
        visualize_positions(theme_name, positions, theme.dimensions[0], theme.dimensions[1])
    
    # Print positioning characteristics
    print(f"\nPositioning Characteristics:")
    
    if theme_name == 'jungle':
        print("  - Ground-based positioning (entities on bottom)")
        print("  - Vertical layering for depth")
        print("  - Small entities can be elevated")
    elif theme_name == 'christmas':
        print("  - Clustered around center (like ornaments on tree)")
        print("  - Some entities float (30% chance)")
        print("  - Cluster radius grows with entity count")
    elif theme_name == 'party':
        print("  - Random distribution across world")
        print("  - Some entities elevated (40% chance)")
        print("  - Elevated entities in top 40% of world")
    elif theme_name == 'school':
        print("  - Row-based structured layout (like desks)")
        print("  - Entities arranged in rows")
        print("  - Aligned positioning within rows")
    elif theme_name == 'ocean':
        print("  - Depth-based layers (surface, mid, deep)")
        print("  - Entities distributed across depth zones")
        print("  - Floating/swimming positions")
    else:
        print("  - Balanced grid distribution")
        print("  - No special positioning rules")
    
    return entities


def compare_themes():
    """Compare positioning across all themes"""
    print(f"\n{'=' * 60}")
    print("THEME POSITIONING COMPARISON")
    print(f"{'=' * 60}")
    
    themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
    
    for theme_name in themes:
        demo_theme_positioning(theme_name, num_entities=8)
        print()


def main():
    """Run the demo"""
    print("\n" + "=" * 60)
    print("THEME-SPECIFIC POSITIONING DEMO")
    print("=" * 60)
    print("\nThis demo shows how different themes position entities")
    print("according to their unique positioning strategies.")
    
    compare_themes()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nKey Observations:")
    print("  - Jungle: Entities cluster near ground (bottom of world)")
    print("  - Christmas: Entities cluster around center")
    print("  - Party: Random distribution with some elevated")
    print("  - School: Structured rows (like classroom desks)")
    print("  - Ocean: Layered by depth (surface/mid/deep)")
    print("  - General: Balanced grid distribution")
    print("\nEach theme creates a unique spatial arrangement that")
    print("matches its thematic context!")
    print()


if __name__ == '__main__':
    main()
