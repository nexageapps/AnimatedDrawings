#!/usr/bin/env python3
"""
Demo script showing the domain models in action.

This script demonstrates creating and using all the domain models
with realistic data.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import models
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from models import (
    User, Theme, ThemedWorld, Drawing, DrawingStatus,
    AnimationData, DrawingEntity, ProcessingJob, JobStatus
)


def main():
    print("=" * 70)
    print("Themed Animation Platform - Domain Models Demo")
    print("=" * 70)
    print()
    
    # Create a user
    print("1. Creating a User...")
    user = User(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="alice@example.com",
        created_at=datetime.now(),
        total_drawings=0
    )
    print(f"   ✓ User created: {user.email}")
    print()
    
    # Create a theme
    print("2. Creating a Theme...")
    theme = Theme(
        id="theme-jungle-001",
        name="jungle",
        display_name="Jungle Adventure",
        background_image_url="/static/backgrounds/jungle.png",
        dimensions=(1920, 1080),
        max_entities=50,
        positioning_rules={
            "type": "ground_based",
            "vertical_layering": True,
            "ground_y": 900
        },
        motion_sequences=["walk", "run", "climb", "swing"]
    )
    print(f"   ✓ Theme created: {theme.display_name}")
    print(f"     - Dimensions: {theme.width}x{theme.height}")
    print(f"     - Max entities: {theme.max_entities}")
    print(f"     - Motion sequences: {', '.join(theme.motion_sequences)}")
    print()
    
    # Create a themed world
    print("3. Creating a Themed World...")
    world = ThemedWorld(
        id="world-jungle-001",
        theme_id=theme.id,
        instance_number=1,
        entity_count=0,
        is_full=False,
        created_at=datetime.now(),
        last_updated=datetime.now()
    )
    print(f"   ✓ World created: {theme.name} instance #{world.instance_number}")
    print(f"     - Occupancy: {world.get_occupancy_rate(theme.max_entities):.1%}")
    print(f"     - Can add entity: {world.can_add_entity(theme.max_entities)}")
    print()
    
    # Create a drawing
    print("4. Creating a Drawing...")
    drawing = Drawing(
        id="drawing-001",
        user_id=user.id,
        original_image_url="/uploads/garlic.png",
        normalized_image_url=None,
        status=DrawingStatus.PENDING,
        theme_id=theme.id,
        created_at=datetime.now(),
        processed_at=None,
        error_message=None
    )
    print(f"   ✓ Drawing created: {drawing.id}")
    print(f"     - Status: {drawing.status.value}")
    print(f"     - Theme: {theme.name}")
    print(f"     - Complete: {drawing.is_complete()}")
    print()
    
    # Create a processing job
    print("5. Creating a Processing Job...")
    job = ProcessingJob(
        id="job-001",
        drawing_id=drawing.id,
        job_type="animation",
        status=JobStatus.QUEUED,
        priority=0,
        attempts=0,
        max_attempts=3,
        error_message=None,
        created_at=datetime.now(),
        started_at=None,
        completed_at=None
    )
    print(f"   ✓ Job created: {job.job_type}")
    print(f"     - Status: {job.status.value}")
    print(f"     - Attempts: {job.attempts}/{job.max_attempts}")
    print()
    
    # Create animation data
    print("6. Creating Animation Data...")
    animation = AnimationData(
        id="anim-001",
        drawing_id=drawing.id,
        character_detected=True,
        segmentation_mask_url="/masks/garlic_mask.png",
        skeleton_data={
            "joints": [
                {"name": "root", "x": 100, "y": 200},
                {"name": "head", "x": 100, "y": 50}
            ]
        },
        motion_sequence="walk",
        animation_file_url="/animations/garlic_walk.mp4",
        sprite_sheet_url="/sprites/garlic_sheet.png"
    )
    print(f"   ✓ Animation created")
    print(f"     - Character detected: {animation.character_detected}")
    print(f"     - Motion: {animation.motion_sequence}")
    print(f"     - Complete: {animation.is_complete()}")
    print(f"     - Has sprite sheet: {animation.has_sprite_sheet()}")
    print()
    
    # Create drawing entities
    print("7. Creating Drawing Entities...")
    entity1 = DrawingEntity(
        id="entity-001",
        drawing_id=drawing.id,
        world_id=world.id,
        position=(100, 700),
        z_index=1,
        dimensions=(150, 200),
        created_at=datetime.now()
    )
    print(f"   ✓ Entity 1 created at ({entity1.x}, {entity1.y})")
    print(f"     - Dimensions: {entity1.width}x{entity1.height}")
    print(f"     - Center: {entity1.get_center()}")
    
    entity2 = DrawingEntity(
        id="entity-002",
        drawing_id="drawing-002",
        world_id=world.id,
        position=(400, 700),
        z_index=1,
        dimensions=(120, 180),
        created_at=datetime.now()
    )
    print(f"   ✓ Entity 2 created at ({entity2.x}, {entity2.y})")
    print()
    
    # Test spatial relationships
    print("8. Testing Spatial Relationships...")
    distance = entity1.distance_to(entity2)
    print(f"   - Distance between entities: {distance:.1f} pixels")
    
    overlaps = entity1.overlaps_with(entity2, min_spacing=50)
    print(f"   - Entities overlap (50px spacing): {overlaps}")
    
    overlaps_no_spacing = entity1.overlaps_with(entity2, min_spacing=0)
    print(f"   - Entities overlap (no spacing): {overlaps_no_spacing}")
    print()
    
    # Demonstrate validation
    print("9. Demonstrating Validation...")
    try:
        invalid_user = User(
            id="test",
            email="invalid-email",
            created_at=datetime.now(),
            total_drawings=0
        )
    except ValueError as e:
        print(f"   ✓ Validation caught invalid email: {e}")
    
    try:
        invalid_theme = Theme(
            id="test",
            name="test",
            display_name="Test",
            background_image_url="/test.png",
            dimensions=(0, 1080),  # Invalid: zero width
            max_entities=50,
            positioning_rules={},
            motion_sequences=["walk"]
        )
    except ValueError as e:
        print(f"   ✓ Validation caught invalid dimensions: {e}")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("All models are working correctly with validation.")
    print("=" * 70)


if __name__ == "__main__":
    main()
