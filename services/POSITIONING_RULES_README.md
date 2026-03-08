# Theme-Specific Positioning Rules

## Overview

This module implements theme-specific positioning strategies for placing drawing entities in themed worlds. Each theme has unique positioning rules that create contextually appropriate spatial arrangements, enhancing the thematic experience.

**Requirements:** 5.1, 6.5

## Architecture

### Base Class: `PositioningRules`

Abstract base class that defines the interface for theme-specific positioning:

- `get_position_constraints()` - Returns constraint parameters for the theme
- `is_valid_position()` - Checks if a position satisfies theme constraints
- `adjust_position_score()` - Adjusts position scores based on theme preferences

### Theme Implementations

#### 1. Jungle Theme (`JunglePositioningRules`)

**Strategy:** Ground-based positioning with vertical layering for depth

**Characteristics:**
- Large entities (height ≥ 100px) must be on ground (bottom 30% of world)
- Small entities (height < 100px) can be elevated (anywhere in bottom 70%)
- Vertical layering creates depth perception
- Prefers positions closer to ground
- Distributes entities across different heights

**Use Case:** Animal characters, explorers, jungle creatures

#### 2. Christmas Theme (`ChristmasPositioningRules`)

**Strategy:** Clustered around center with some floating

**Characteristics:**
- Entities cluster around world center (like ornaments on a tree)
- Cluster radius grows with entity count
- 30% chance for entities to float (can be placed anywhere)
- Non-floating entities must be within cluster radius
- Floating entities prefer top area of world

**Use Case:** Ornaments, presents, festive characters

#### 3. Party Theme (`PartyPositioningRules`)

**Strategy:** Random distribution with some elevated

**Characteristics:**
- Random distribution across entire world
- 40% chance for entities to be elevated
- Elevated entities prefer top 40% of world (like balloons)
- Adds randomness to position scores for varied placement
- No strict positioning constraints

**Use Case:** Party guests, balloons, decorations

#### 4. School Theme (`SchoolPositioningRules`)

**Strategy:** Row-based structured layout

**Characteristics:**
- Entities arranged in rows (like desks in a classroom)
- Row height: 150 pixels
- Calculates target row and column based on entity count
- Rewards positions close to ideal row/column alignment
- Creates structured, organized appearance

**Use Case:** Students, desks, classroom objects

#### 5. Ocean Theme (`OceanPositioningRules`)

**Strategy:** Depth-based layers with floating positions

**Characteristics:**
- Three depth layers:
  - Surface: top 20%
  - Mid-water: 20-60%
  - Deep: 60-100%
- Entities randomly assigned to a depth layer
- Must stay within assigned layer
- Prefers middle of assigned layer
- Creates underwater depth perception

**Use Case:** Fish, sea creatures, underwater objects

#### 6. General Theme (`GeneralPositioningRules`)

**Strategy:** Balanced grid distribution (default)

**Characteristics:**
- No special positioning constraints
- Uses base positioning algorithm only
- Balanced distribution across world
- Default fallback for unknown themes

**Use Case:** Generic content, mixed themes

## Integration with World Compositor

The `WorldCompositorService` integrates positioning rules into its `calculate_position()` method:

```python
# Get theme-specific positioning rules
positioning_rules = get_positioning_rules(theme.name)
constraints = positioning_rules.get_position_constraints(
    entity_width, entity_height, world_width, world_height, existing_entities
)

# Check theme-specific constraints
if not positioning_rules.is_valid_position(
    x, y, entity_width, entity_height,
    world_width, world_height, constraints
):
    continue  # Skip invalid positions

# Apply theme-specific score adjustments
adjusted_score = positioning_rules.adjust_position_score(
    base_score, x, y, entity_width, entity_height,
    world_width, world_height, existing_entities, constraints
)
```

## Usage Example

```python
from services.world_compositor_service import WorldCompositorService
from services.positioning_rules import get_positioning_rules

# Create service
service = WorldCompositorService()

# Calculate position for jungle theme
position = service.calculate_position(
    world=jungle_world,
    theme=jungle_theme,
    entity_width=150,
    entity_height=200,
    existing_entities=[]
)

# Position will follow jungle ground-based rules
print(f"Entity placed at: {position}")
```

## Testing

### Unit Tests: `test_positioning_rules.py`

Comprehensive tests for each theme:

- Factory function returns correct rules
- Jungle ground-based positioning
- Christmas clustered positioning
- Party random distribution
- School row-based positioning
- Ocean depth-based layers
- Integration with World Compositor
- Theme-specific score adjustments

Run tests:
```bash
python services/test_positioning_rules.py
```

### Demo: `demo_theme_positioning.py`

Visual demonstration of positioning strategies:

- Places 8 entities in each theme
- Shows ASCII visualization of positions
- Compares positioning across all themes

Run demo:
```bash
python services/demo_theme_positioning.py
```

## Design Decisions

### Why Abstract Base Class?

- Enforces consistent interface across themes
- Makes it easy to add new themes
- Allows theme-specific customization while maintaining compatibility

### Why Three Methods?

1. **`get_position_constraints()`** - Calculates theme-specific parameters once per entity
2. **`is_valid_position()`** - Fast filtering of invalid positions (called many times)
3. **`adjust_position_score()`** - Fine-tunes scoring for theme preferences

This separation optimizes performance by calculating constraints once and using them for many position checks.

### Why Randomness in Some Themes?

- **Christmas floating:** Creates variety (some ornaments, some tree toppers)
- **Party elevation:** Mimics real parties (some balloons float, some decorations on ground)
- **Ocean layers:** Distributes entities across depth zones naturally

Randomness is seeded per entity placement, creating consistent but varied results.

## Performance Considerations

- Constraints calculated once per entity placement
- Position validation is O(1) for most themes
- Score adjustment is O(n) where n = existing entities
- Grid-based collision detection remains efficient

## Future Enhancements

Potential improvements:

1. **Configurable parameters** - Allow themes to specify parameters (e.g., cluster radius, row height)
2. **Dynamic rules** - Rules that adapt based on world occupancy
3. **Multi-layer support** - Entities in multiple depth layers simultaneously
4. **Animation-aware positioning** - Consider animation motion when placing
5. **User preferences** - Allow users to influence positioning (e.g., "place near friend's drawing")

## Files

- `services/positioning_rules.py` - Core implementation
- `services/world_compositor_service.py` - Integration with compositor
- `services/test_positioning_rules.py` - Unit tests
- `services/demo_theme_positioning.py` - Visual demonstration
- `services/POSITIONING_RULES_README.md` - This documentation

## Related Requirements

- **Requirement 5.1:** Theme-based world placement
- **Requirement 6.5:** Theme-specific positioning rules
- **Property 14:** Theme-Based World Placement

## Summary

Theme-specific positioning rules create contextually appropriate spatial arrangements that enhance the thematic experience. Each theme implements unique positioning strategies:

- **Jungle:** Ground-based with vertical layering
- **Christmas:** Clustered around center
- **Party:** Random with elevation
- **School:** Structured rows
- **Ocean:** Depth-based layers
- **General:** Balanced grid

The system is extensible, performant, and well-tested, providing a solid foundation for themed world composition.
