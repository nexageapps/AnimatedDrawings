# World Compositor Service

## Overview

The World Compositor Service is responsible for spatial positioning of drawing entities within themed worlds. It implements an intelligent placement algorithm that ensures optimal distribution of entities while maintaining minimum spacing requirements and preventing collisions.

## Features

### Core Functionality

1. **Grid-Based Collision Detection**
   - Efficient spatial indexing using occupancy grid
   - Fast collision checking for entity placement
   - Configurable grid step size (default: 25 pixels)

2. **Position Scoring Algorithm**
   - Evaluates potential positions based on multiple criteria
   - Considers distance from existing entities
   - Balances distribution across world quadrants
   - Applies slight center bias for aesthetic placement

3. **Minimum Spacing Enforcement**
   - Enforces 50-pixel minimum spacing between entities (Requirement 5.3)
   - Prevents visual overlap and crowding
   - Configurable spacing parameter

4. **Entity Size Consideration**
   - Accounts for entity dimensions during placement (Requirement 6.1)
   - Validates entities fit within world bounds
   - Handles variable entity sizes gracefully

## Implementation Details

### Spatial Positioning Algorithm

The algorithm follows these steps:

1. **Validation**: Check if entity fits within world dimensions
2. **Grid Building**: Create occupancy grid from existing entities
3. **Position Search**: Iterate through potential positions using grid step
4. **Collision Detection**: Check each position for collisions with existing entities
5. **Position Scoring**: Calculate score for each valid position
6. **Selection**: Choose position with highest score

### Position Scoring Criteria

The scoring algorithm considers:

- **Distance from other entities** (50% weight)
  - Minimum distance to nearest entity
  - Average distance to all entities
  - Prefers positions with more spacing

- **Distribution balance** (30% weight)
  - Divides world into quadrants
  - Penalizes overcrowded quadrants
  - Promotes even distribution

- **Center bias** (20% weight)
  - Slight preference for central positions
  - Avoids extreme edge placement
  - Creates more natural-looking scenes

### Collision Detection

Uses axis-aligned bounding box (AABB) collision detection with minimum spacing:

```python
# Expand first rectangle by min_spacing
expanded_box = (x1 - spacing, y1 - spacing, 
                x1 + w1 + spacing, y1 + h1 + spacing)

# Check for overlap with second rectangle
if expanded_box overlaps with (x2, y2, x2 + w2, y2 + h2):
    collision = True
```

## Usage

### Basic Usage

```python
from services.world_compositor_service import WorldCompositorService
from models.themed_world import ThemedWorld
from models.theme import Theme

# Initialize service
compositor = WorldCompositorService()

# Calculate position for new entity
position = compositor.calculate_position(
    world=world,
    theme=theme,
    entity_width=150,
    entity_height=200,
    existing_entities=existing_entities
)

if position:
    # Place entity at calculated position
    entity = compositor.place_entity(
        world_id=world.id,
        drawing_id=drawing.id,
        position=position,
        dimensions=(150, 200),
        z_index=0
    )
```

### Retrieving World Entities

```python
# Get all entities in a world
entities = compositor.get_world_entities(world_id)

# Use entities for collision detection
new_position = compositor.calculate_position(
    world, theme, 100, 100, existing_entities=entities
)
```

## Configuration

### Constants

- `MIN_SPACING`: Minimum spacing between entities (default: 50 pixels)
- `GRID_STEP`: Grid step size for position search (default: 25 pixels)

### Adjusting Parameters

```python
# Modify minimum spacing
compositor.MIN_SPACING = 75  # Increase spacing to 75 pixels

# Modify grid step (smaller = more precise but slower)
compositor.GRID_STEP = 10  # More granular position search
```

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
python services/test_world_compositor.py
```

Tests cover:
- Minimum spacing enforcement
- Position validation (bounds checking)
- Position calculation in empty worlds
- Position calculation with existing entities
- Position scoring algorithm
- Grid-based collision detection
- Edge cases (entity too large, world at capacity)

### Demo Script

Run the interactive demonstration:

```bash
python services/demo_world_compositor.py
```

Demonstrates:
- Progressive entity placement
- Collision detection visualization
- Position scoring comparison
- ASCII visualization of world layout

## Performance Characteristics

### Time Complexity

- **Position calculation**: O(n × m) where:
  - n = number of grid positions to check
  - m = number of existing entities
  
- **Grid building**: O(e × g) where:
  - e = number of existing entities
  - g = grid cells per entity

### Space Complexity

- **Occupancy grid**: O(w × h / s²) where:
  - w = world width
  - h = world height
  - s = grid step size

### Optimization Strategies

1. **Grid-based indexing**: Reduces collision checks from O(n²) to O(n × k) where k is average entities per grid cell
2. **Early termination**: Stops searching when sufficient candidates found
3. **Configurable grid step**: Balance between precision and performance

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 5.2**: Assigns spatial coordinates to each drawing entity
- **Requirement 5.3**: Prevents overlap by maintaining minimum spacing of 50 pixels
- **Requirement 6.1**: Considers entity visual characteristics (size) when assigning coordinates

## Integration Points

### Database Integration

- Uses SQLAlchemy ORM for entity persistence
- Automatically updates world entity count
- Maintains entity creation timestamps

### Service Dependencies

- **ThemeManagerService**: Retrieves theme dimensions and properties
- **Database ORM**: Persists entities and updates world state

### Model Dependencies

- **ThemedWorld**: World instance with capacity tracking
- **DrawingEntity**: Entity with position and dimensions
- **Theme**: Theme configuration with world dimensions

## Future Enhancements

Potential improvements for future iterations:

1. **Theme-specific positioning rules**
   - Ground-based positioning for jungle theme
   - Clustered positioning for christmas theme
   - Row-based positioning for school theme

2. **Advanced scoring algorithms**
   - Machine learning-based position optimization
   - User preference learning
   - Aesthetic composition rules

3. **Performance optimizations**
   - Spatial indexing (quadtree, R-tree)
   - Parallel position evaluation
   - Caching of occupancy grids

4. **Visual balance improvements**
   - Color distribution consideration
   - Size-based clustering
   - Dynamic spacing based on entity importance

## Troubleshooting

### No Valid Position Found

If `calculate_position()` returns `None`:

1. **World is full**: Too many entities, no space available
   - Solution: Create new world instance
   
2. **Entity too large**: Entity dimensions exceed world dimensions
   - Solution: Resize entity or use larger world
   
3. **Grid step too large**: Missing valid positions between grid points
   - Solution: Reduce `GRID_STEP` for finer granularity

### Poor Position Distribution

If entities cluster in one area:

1. **Adjust scoring weights**: Modify distribution balance weight
2. **Reduce center bias**: Lower center bias weight in scoring
3. **Increase minimum spacing**: Force more spread-out placement

## References

- Design Document: `.kiro/specs/themed-animation-platform/design.md`
- Requirements Document: `.kiro/specs/themed-animation-platform/requirements.md`
- Task Definition: `.kiro/specs/themed-animation-platform/tasks.md` (Task 6.1)
