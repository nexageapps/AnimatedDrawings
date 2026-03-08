# Domain Models

This directory contains the core domain models for the Themed Animation Platform. These models represent the business entities in the system and match the database schema defined in `database/migrations/001_initial_schema.sql`.

## Overview

The domain models are implemented as Python dataclasses with built-in validation logic. Each model includes:

- Type-safe attributes using Python type hints
- Validation methods that enforce business rules
- Helper methods for common operations
- Automatic validation on initialization

## Models

### User (`user.py`)

Represents a user in the system, identified by email address.

**Attributes:**
- `id`: Unique identifier (UUID)
- `email`: User's email address (validated format)
- `created_at`: Timestamp when user was created
- `total_drawings`: Count of drawings submitted by this user

**Validation:**
- Email must match valid email format
- `total_drawings` must be non-negative

### Drawing (`drawing.py`)

Represents a drawing submission with its processing status.

**Attributes:**
- `id`: Unique identifier (UUID)
- `user_id`: ID of the user who submitted the drawing
- `original_image_url`: URL/path to the original uploaded image
- `normalized_image_url`: URL/path to the normalized/processed image
- `status`: Current processing status (DrawingStatus enum)
- `theme_id`: ID of the theme assigned to this drawing
- `created_at`: Timestamp when drawing was submitted
- `processed_at`: Timestamp when processing completed
- `error_message`: Error details if processing failed

**Status Values:**
- `PENDING`: Drawing has been received but not yet processed
- `PROCESSING`: Drawing is currently being processed
- `ANIMATED`: Drawing has been successfully animated
- `FAILED`: Processing failed

**Validation:**
- `original_image_url` cannot be empty
- `processed_at` must be after `created_at`
- Failed drawings must have an `error_message`

**Helper Methods:**
- `is_complete()`: Check if processing is complete (success or failure)
- `is_successful()`: Check if drawing was successfully animated

### Theme (`theme.py`)

Represents a themed environment with its properties and rules.

**Attributes:**
- `id`: Unique identifier (UUID)
- `name`: Internal theme name (e.g., 'jungle', 'christmas')
- `display_name`: Human-readable theme name
- `background_image_url`: URL/path to the theme's background image
- `dimensions`: Tuple of (width, height) in pixels
- `max_entities`: Maximum number of entities allowed in a world
- `positioning_rules`: Dictionary containing positioning algorithm rules
- `motion_sequences`: List of motion sequence names available for this theme

**Validation:**
- `name` and `display_name` cannot be empty
- Dimensions must be positive
- `max_entities` must be positive
- `motion_sequences` cannot be empty

**Helper Methods:**
- `width` and `height` properties for easy access to dimensions
- `has_motion_sequence(motion)`: Check if theme supports a motion

### ThemedWorld (`themed_world.py`)

Represents an instance of a themed world where drawings are placed.

**Attributes:**
- `id`: Unique identifier (UUID)
- `theme_id`: ID of the theme this world belongs to
- `instance_number`: Instance number for this theme (1, 2, 3, ...)
- `entity_count`: Current number of entities in this world
- `is_full`: Whether this world has reached capacity
- `created_at`: Timestamp when world was created
- `last_updated`: Timestamp of last modification

**Validation:**
- `instance_number` must be positive
- `entity_count` must be non-negative
- `last_updated` must be after or equal to `created_at`

**Helper Methods:**
- `can_add_entity(max_entities)`: Check if world can accept another entity
- `get_occupancy_rate(max_entities)`: Calculate occupancy rate (0.0 to 1.0)

### AnimationData (`animation_data.py`)

Represents the animation processing results for a drawing.

**Attributes:**
- `id`: Unique identifier (UUID)
- `drawing_id`: ID of the drawing this animation belongs to
- `character_detected`: Whether a character was successfully detected
- `segmentation_mask_url`: URL/path to the segmentation mask image
- `skeleton_data`: Dictionary containing skeleton/joint data
- `motion_sequence`: Name of the motion sequence applied
- `animation_file_url`: URL/path to the animation output file
- `sprite_sheet_url`: URL/path to the sprite sheet (if generated)

**Validation:**
- When `character_detected` is True, the following fields are required:
  - `segmentation_mask_url`
  - `skeleton_data`
  - `motion_sequence`
  - `animation_file_url`

**Helper Methods:**
- `is_complete()`: Check if animation processing is complete
- `has_sprite_sheet()`: Check if a sprite sheet was generated

### DrawingEntity (`drawing_entity.py`)

Represents a drawing placed within a themed world with spatial coordinates.

**Attributes:**
- `id`: Unique identifier (UUID)
- `drawing_id`: ID of the drawing this entity represents
- `world_id`: ID of the world this entity is placed in
- `position`: Tuple of (x, y) coordinates in pixels
- `z_index`: Z-order for layering (higher values appear in front)
- `dimensions`: Tuple of (width, height) in pixels
- `created_at`: Timestamp when entity was placed

**Validation:**
- Position coordinates must be non-negative
- Dimensions must be positive

**Helper Methods:**
- `x`, `y`, `width`, `height` properties for easy access
- `get_bounding_box()`: Get (x1, y1, x2, y2) bounding box
- `get_center()`: Get center point coordinates
- `distance_to(other)`: Calculate distance to another entity
- `overlaps_with(other, min_spacing)`: Check for overlap with another entity

### ProcessingJob (`processing_job.py`)

Represents a background processing job in the queue.

**Attributes:**
- `id`: Unique identifier (UUID)
- `drawing_id`: ID of the drawing being processed
- `job_type`: Type of job (image_processing, animation, composition)
- `status`: Current job status (JobStatus enum)
- `priority`: Job priority (higher values processed first)
- `attempts`: Number of processing attempts made
- `max_attempts`: Maximum number of attempts before permanent failure
- `error_message`: Error details if job failed
- `created_at`: Timestamp when job was created
- `started_at`: Timestamp when job processing started
- `completed_at`: Timestamp when job completed

**Job Types:**
- `image_processing`: Image validation and normalization
- `animation`: Character detection and animation generation
- `composition`: World placement and composition

**Status Values:**
- `QUEUED`: Job is waiting to be processed
- `PROCESSING`: Job is currently being processed
- `COMPLETED`: Job completed successfully
- `FAILED`: Job failed

**Validation:**
- `job_type` must be one of the valid types
- `attempts` must be non-negative and not exceed `max_attempts`
- `max_attempts` must be positive
- Timestamps must be in logical order
- Failed jobs must have an `error_message`

**Helper Methods:**
- `is_complete()`: Check if job is complete (success or failure)
- `is_successful()`: Check if job completed successfully
- `can_retry()`: Check if job can be retried
- `should_retry()`: Check if job should be retried
- `get_processing_duration()`: Get processing duration in seconds

## Usage Examples

### Creating a User

```python
from models import User
from datetime import datetime

user = User(
    id="123e4567-e89b-12d3-a456-426614174000",
    email="user@example.com",
    created_at=datetime.now(),
    total_drawings=0
)
```

### Creating a Drawing

```python
from models import Drawing, DrawingStatus
from datetime import datetime

drawing = Drawing(
    id="drawing-123",
    user_id="user-123",
    original_image_url="/uploads/image.png",
    normalized_image_url=None,
    status=DrawingStatus.PENDING,
    theme_id="theme-jungle",
    created_at=datetime.now(),
    processed_at=None,
    error_message=None
)

# Check status
if drawing.is_complete():
    print("Drawing processing is complete")
```

### Working with Themes

```python
from models import Theme

theme = Theme(
    id="theme-jungle",
    name="jungle",
    display_name="Jungle Adventure",
    background_image_url="/static/backgrounds/jungle.png",
    dimensions=(1920, 1080),
    max_entities=50,
    positioning_rules={"type": "ground_based", "vertical_layering": True},
    motion_sequences=["walk", "run", "climb", "swing"]
)

# Check if theme supports a motion
if theme.has_motion_sequence("walk"):
    print("Theme supports walking animation")
```

### Checking Entity Overlap

```python
from models import DrawingEntity
from datetime import datetime

entity1 = DrawingEntity(
    id="entity-1",
    drawing_id="drawing-1",
    world_id="world-123",
    position=(100, 200),
    z_index=1,
    dimensions=(150, 200),
    created_at=datetime.now()
)

entity2 = DrawingEntity(
    id="entity-2",
    drawing_id="drawing-2",
    world_id="world-123",
    position=(200, 300),
    z_index=1,
    dimensions=(150, 200),
    created_at=datetime.now()
)

# Check for overlap with minimum spacing
if entity1.overlaps_with(entity2, min_spacing=50):
    print("Entities are too close together")
```

### Managing Processing Jobs

```python
from models import ProcessingJob, JobStatus
from datetime import datetime

job = ProcessingJob(
    id="job-123",
    drawing_id="drawing-123",
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

# Check if job can be retried after failure
if job.status == JobStatus.FAILED and job.can_retry():
    print(f"Job can be retried ({job.attempts}/{job.max_attempts} attempts)")
```

## Testing

Unit tests for all models are provided in `test_models.py`. Run tests with:

```bash
python3 -m pytest models/test_models.py -v
```

The tests cover:
- Valid model creation
- Validation logic
- Edge cases and error conditions
- Helper methods
- Enum conversions

## Requirements

This implementation satisfies the following requirements:
- **Requirement 2.2**: Image storage with unique identifiers and metadata
- **Requirement 9.1**: Drawing entity metadata persistence

## Integration

These models are designed to work with:
- SQLAlchemy ORM for database persistence (see `database/connection.py`)
- REST API endpoints for serialization
- Background job processing with Celery
- Theme management and world composition services

## Notes

- All models use Python dataclasses for clean, concise code
- Validation is performed automatically on initialization via `__post_init__`
- Enums are used for status fields to ensure type safety
- Helper methods provide convenient access to computed properties
- Models are immutable by default (use `replace()` to create modified copies)
