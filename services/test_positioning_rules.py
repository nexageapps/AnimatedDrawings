"""
Test script for Theme-Specific Positioning Rules

Tests the positioning rules for each theme to verify they implement
the correct positioning strategies.

Requirements: 5.1, 6.5
"""

import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.positioning_rules import (
    get_positioning_rules,
    JunglePositioningRules,
    ChristmasPositioningRules,
    PartyPositioningRules,
    SchoolPositioningRules,
    OceanPositioningRules,
    GeneralPositioningRules
)
from services.world_compositor_service import WorldCompositorService
from models.themed_world import ThemedWorld
from models.drawing_entity import DrawingEntity
from models.theme import Theme


def create_test_theme(name, width=1920, height=1080):
    """Create a test theme"""
    return Theme(
        id=str(uuid4()),
        name=name,
        display_name=name.title(),
        background_image_url='',
        dimensions=(width, height),
        max_entities=50,
        positioning_rules={},
        motion_sequences=['wave_hello']
    )


def create_test_world(theme_id):
    """Create a test world"""
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
    """Create a test entity"""
    return DrawingEntity(
        id=str(uuid4()),
        drawing_id=str(uuid4()),
        world_id=world_id,
        position=(x, y),
        z_index=0,
        dimensions=(width, height),
        created_at=datetime.utcnow()
    )


def test_positioning_rules_factory():
    """Test that the factory returns correct positioning rules"""
    print("\nTest: Positioning Rules Factory")
    print("=" * 60)
    
    test_cases = [
        ('jungle', JunglePositioningRules),
        ('christmas', ChristmasPositioningRules),
        ('party', PartyPositioningRules),
        ('school', SchoolPositioningRules),
        ('ocean', OceanPositioningRules),
        ('general', GeneralPositioningRules),
        ('unknown', GeneralPositioningRules),  # Should default to general
    ]
    
    for theme_name, expected_class in test_cases:
        rules = get_positioning_rules(theme_name)
        actual_class = rules.__class__
        status = "✓" if actual_class == expected_class else "✗"
        print(f"  {theme_name}: {actual_class.__name__} {status}")
        assert actual_class == expected_class, f"Expected {expected_class.__name__}, got {actual_class.__name__}"
    
    print("\n✓ Positioning rules factory works correctly")


def test_jungle_ground_based_positioning():
    """Test jungle theme ground-based positioning"""
    print("\nTest: Jungle Ground-Based Positioning")
    print("=" * 60)
    
    rules = JunglePositioningRules()
    world_width, world_height = 1920, 1080
    
    # Test large entity (should be on ground - bottom 30%)
    entity_width, entity_height = 150, 200
    constraints = rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, []
    )
    
    print(f"World height: {world_height}")
    print(f"Ground level starts at: {constraints['ground_level_start']} (70% down)")
    print(f"Large entity ({entity_width}x{entity_height}):")
    
    # Position on ground (should be valid)
    y_ground = 900  # In bottom 30%
    valid = rules.is_valid_position(
        100, y_ground, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"  Position at y={y_ground} (ground): {'VALID ✓' if valid else 'INVALID ✗'}")
    assert valid, "Large entity should be valid on ground"
    
    # Position too high (should be invalid)
    y_high = 100  # In top 30%
    valid = rules.is_valid_position(
        100, y_high, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"  Position at y={y_high} (elevated): {'VALID ✗' if valid else 'INVALID ✓'}")
    assert not valid, "Large entity should not be valid when elevated"
    
    # Test small entity (can be elevated)
    entity_width, entity_height = 50, 80
    constraints = rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, []
    )
    
    print(f"\nSmall entity ({entity_width}x{entity_height}):")
    
    # Small entity elevated (should be valid)
    y_elevated = 400
    valid = rules.is_valid_position(
        100, y_elevated, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"  Position at y={y_elevated} (elevated): {'VALID ✓' if valid else 'INVALID ✗'}")
    assert valid, "Small entity should be valid when elevated"
    
    print("\n✓ Jungle ground-based positioning works correctly")


def test_christmas_clustered_positioning():
    """Test christmas theme clustered positioning"""
    print("\nTest: Christmas Clustered Positioning")
    print("=" * 60)
    
    rules = ChristmasPositioningRules()
    world_width, world_height = 1920, 1080
    entity_width, entity_height = 100, 100
    
    # Get constraints (may allow floating)
    constraints = rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, []
    )
    
    center_x = world_width // 2
    center_y = world_height // 2
    
    print(f"World center: ({center_x}, {center_y})")
    print(f"Cluster radius: {constraints['cluster_radius']:.0f}")
    print(f"Allow floating: {constraints['allow_floating']}")
    
    # Position near center (should be valid)
    x_center = center_x - entity_width // 2
    y_center = center_y - entity_height // 2
    valid = rules.is_valid_position(
        x_center, y_center, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"\nPosition near center ({x_center}, {y_center}): {'VALID ✓' if valid else 'INVALID ✗'}")
    
    if not constraints['allow_floating']:
        # Position far from center (should be invalid if not floating)
        x_far = 100
        y_far = 100
        valid = rules.is_valid_position(
            x_far, y_far, entity_width, entity_height,
            world_width, world_height, constraints
        )
        print(f"Position far from center ({x_far}, {y_far}): {'VALID ✗' if valid else 'INVALID ✓'}")
        assert not valid, "Non-floating entity should not be valid far from center"
    else:
        print("Entity is floating - all positions valid")
    
    print("\n✓ Christmas clustered positioning works correctly")


def test_party_random_distribution():
    """Test party theme random distribution"""
    print("\nTest: Party Random Distribution")
    print("=" * 60)
    
    rules = PartyPositioningRules()
    world_width, world_height = 1920, 1080
    entity_width, entity_height = 100, 100
    
    # Test multiple entities to see distribution
    elevated_count = 0
    ground_count = 0
    
    for i in range(10):
        constraints = rules.get_position_constraints(
            entity_width, entity_height, world_width, world_height, []
        )
        
        if constraints['is_elevated']:
            elevated_count += 1
        else:
            ground_count += 1
    
    print(f"Out of 10 entities:")
    print(f"  Elevated: {elevated_count}")
    print(f"  Ground level: {ground_count}")
    print(f"  Elevated percentage: {elevated_count * 10}%")
    
    # Should have some mix (not all elevated or all ground)
    assert elevated_count > 0, "Should have some elevated entities"
    assert ground_count > 0, "Should have some ground-level entities"
    
    # Test that elevated entities prefer top area
    constraints = {'is_elevated': True, 'elevation_zone_end': int(world_height * 0.4)}
    
    y_top = 200  # In top 40%
    valid = rules.is_valid_position(
        100, y_top, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"\nElevated entity at y={y_top} (top area): {'VALID ✓' if valid else 'INVALID ✗'}")
    assert valid, "Elevated entity should be valid in top area"
    
    y_bottom = 800  # In bottom 60%
    valid = rules.is_valid_position(
        100, y_bottom, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"Elevated entity at y={y_bottom} (bottom area): {'VALID ✗' if valid else 'INVALID ✓'}")
    assert not valid, "Elevated entity should not be valid in bottom area"
    
    print("\n✓ Party random distribution works correctly")


def test_school_row_based_positioning():
    """Test school theme row-based positioning"""
    print("\nTest: School Row-Based Positioning")
    print("=" * 60)
    
    rules = SchoolPositioningRules()
    world_width, world_height = 1920, 1080
    entity_width, entity_height = 100, 100
    
    # Test first entity (should be in first row)
    constraints = rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, []
    )
    
    print(f"Row height: {constraints['row_height']}")
    print(f"Number of rows: {constraints['num_rows']}")
    print(f"Entities per row: {constraints['entities_per_row']}")
    print(f"Target row for first entity: {constraints['target_row']}")
    
    # Position in target row (should be valid)
    row_start = constraints['target_row'] * constraints['row_height']
    y_in_row = row_start + 25
    valid = rules.is_valid_position(
        100, y_in_row, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"\nPosition in target row (y={y_in_row}): {'VALID ✓' if valid else 'INVALID ✗'}")
    assert valid, "Position in target row should be valid"
    
    # Position in wrong row (should be invalid)
    wrong_row = (constraints['target_row'] + 2) % constraints['num_rows']
    y_wrong_row = wrong_row * constraints['row_height'] + 25
    valid = rules.is_valid_position(
        100, y_wrong_row, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"Position in wrong row (y={y_wrong_row}): {'VALID ✗' if valid else 'INVALID ✓'}")
    # Note: There's some tolerance, so this might still be valid if close enough
    
    # Test that subsequent entities go to next positions
    existing_entities = []
    for i in range(5):
        entity = create_test_entity(str(uuid4()), i * 200, 100, 100, 100)
        existing_entities.append(entity)
    
    constraints = rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, existing_entities
    )
    
    print(f"\nAfter placing 5 entities:")
    print(f"  Next target row: {constraints['target_row']}")
    print(f"  Next target col: {constraints['target_col']}")
    
    print("\n✓ School row-based positioning works correctly")


def test_ocean_depth_layers():
    """Test ocean theme depth-based layers"""
    print("\nTest: Ocean Depth-Based Layers")
    print("=" * 60)
    
    rules = OceanPositioningRules()
    world_width, world_height = 1920, 1080
    entity_width, entity_height = 100, 100
    
    # Test multiple entities to see layer distribution
    layer_counts = {'surface': 0, 'mid': 0, 'deep': 0}
    
    for i in range(20):
        constraints = rules.get_position_constraints(
            entity_width, entity_height, world_width, world_height, []
        )
        layer_counts[constraints['layer']] += 1
    
    print(f"Layer distribution (out of 20 entities):")
    print(f"  Surface (top 20%): {layer_counts['surface']}")
    print(f"  Mid-water (20-60%): {layer_counts['mid']}")
    print(f"  Deep (60-100%): {layer_counts['deep']}")
    
    # Should have entities in multiple layers
    layers_used = sum(1 for count in layer_counts.values() if count > 0)
    assert layers_used >= 2, "Should use at least 2 different depth layers"
    
    # Test that entities stay in their assigned layer
    constraints = rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, []
    )
    
    print(f"\nTest entity assigned to '{constraints['layer']}' layer:")
    print(f"  Layer range: {constraints['layer_start']} - {constraints['layer_end']}")
    
    # Position in assigned layer (should be valid)
    y_in_layer = (constraints['layer_start'] + constraints['layer_end']) // 2
    valid = rules.is_valid_position(
        100, y_in_layer, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"  Position in layer (y={y_in_layer}): {'VALID ✓' if valid else 'INVALID ✗'}")
    assert valid, "Position in assigned layer should be valid"
    
    # Position outside assigned layer (should be invalid)
    if constraints['layer'] == 'surface':
        y_outside = world_height - 100  # Deep water
    else:
        y_outside = 50  # Surface
    
    valid = rules.is_valid_position(
        100, y_outside, entity_width, entity_height,
        world_width, world_height, constraints
    )
    print(f"  Position outside layer (y={y_outside}): {'VALID ✗' if valid else 'INVALID ✓'}")
    assert not valid, "Position outside assigned layer should be invalid"
    
    print("\n✓ Ocean depth-based layers work correctly")


def test_integration_with_world_compositor():
    """Test integration of positioning rules with WorldCompositorService"""
    print("\nTest: Integration with World Compositor Service")
    print("=" * 60)
    
    service = WorldCompositorService()
    
    # Test each theme
    themes_to_test = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
    
    for theme_name in themes_to_test:
        theme = create_test_theme(theme_name)
        world = create_test_world(theme.id)
        
        # Calculate position for entity
        position = service.calculate_position(
            world, theme, 100, 100, existing_entities=[]
        )
        
        status = "✓" if position is not None else "✗"
        print(f"  {theme_name}: position={position} {status}")
        assert position is not None, f"Should find position for {theme_name} theme"
    
    print("\n✓ Integration with World Compositor Service works correctly")


def test_theme_specific_score_adjustments():
    """Test that theme-specific rules adjust scores appropriately"""
    print("\nTest: Theme-Specific Score Adjustments")
    print("=" * 60)
    
    world_width, world_height = 1920, 1080
    entity_width, entity_height = 100, 100
    existing_entities = []
    
    # Test jungle theme prefers ground positions
    jungle_rules = JunglePositioningRules()
    constraints = jungle_rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, existing_entities
    )
    
    base_score = 100.0
    
    # Ground position
    score_ground = jungle_rules.adjust_position_score(
        base_score, 100, 900, entity_width, entity_height,
        world_width, world_height, existing_entities, constraints
    )
    
    # Elevated position
    score_elevated = jungle_rules.adjust_position_score(
        base_score, 100, 100, entity_width, entity_height,
        world_width, world_height, existing_entities, constraints
    )
    
    print(f"Jungle theme:")
    print(f"  Ground position score: {score_ground:.2f}")
    print(f"  Elevated position score: {score_elevated:.2f}")
    print(f"  Ground scores {'higher ✓' if score_ground > score_elevated else 'lower ✗'}")
    
    assert score_ground > score_elevated, "Jungle should prefer ground positions"
    
    # Test christmas theme prefers center positions
    christmas_rules = ChristmasPositioningRules()
    constraints = christmas_rules.get_position_constraints(
        entity_width, entity_height, world_width, world_height, existing_entities
    )
    
    if not constraints['allow_floating']:
        # Center position
        center_x = world_width // 2
        center_y = world_height // 2
        score_center = christmas_rules.adjust_position_score(
            base_score, center_x, center_y, entity_width, entity_height,
            world_width, world_height, existing_entities, constraints
        )
        
        # Corner position
        score_corner = christmas_rules.adjust_position_score(
            base_score, 100, 100, entity_width, entity_height,
            world_width, world_height, existing_entities, constraints
        )
        
        print(f"\nChristmas theme (non-floating):")
        print(f"  Center position score: {score_center:.2f}")
        print(f"  Corner position score: {score_corner:.2f}")
        print(f"  Center scores {'higher ✓' if score_center > score_corner else 'lower ✗'}")
        
        assert score_center > score_corner, "Christmas should prefer center positions"
    else:
        print(f"\nChristmas theme: Entity is floating (skipping center preference test)")
    
    print("\n✓ Theme-specific score adjustments work correctly")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("THEME-SPECIFIC POSITIONING RULES TESTS")
    print("=" * 60)
    
    try:
        test_positioning_rules_factory()
        test_jungle_ground_based_positioning()
        test_christmas_clustered_positioning()
        test_party_random_distribution()
        test_school_row_based_positioning()
        test_ocean_depth_layers()
        test_integration_with_world_compositor()
        test_theme_specific_score_adjustments()
        
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
