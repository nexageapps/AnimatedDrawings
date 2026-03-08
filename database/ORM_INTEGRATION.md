# ORM Integration Documentation

## Overview

This document describes the SQLAlchemy ORM layer, database connection pooling, and repository pattern implementation for the Themed Animation Platform.

**Requirements:** 9.2 - THE Server SHALL maintain a database of all Themed_World instances and their associated Drawing_Entity instances

## Architecture

The database layer consists of three main components:

1. **Connection Management** (`connection.py`) - Handles database connections and pooling
2. **ORM Models** (`orm.py`) - SQLAlchemy ORM mappings for domain models
3. **Repository Pattern** (`repository.py`) - Data access abstraction layer

## 1. Connection Management

### Features

- **Connection Pooling**: Uses SQLAlchemy's connection pool with configurable size
- **Pre-ping**: Verifies connections before use to handle stale connections
- **Connection Recycling**: Automatically recycles connections after 1 hour
- **Context Managers**: Provides safe connection and session management

### Configuration

```python
from database.orm import init_db

# Initialize with custom pool settings
init_db(
    connection_string='postgresql://user:pass@localhost/dbname',
    echo=False,              # Set to True for SQL logging
    pool_size=10,            # Number of connections to maintain
    max_overflow=20          # Additional connections when pool is full
)
```

### Usage

```python
from database.orm import get_session

# Get a session
session = get_session()
try:
    # Perform database operations
    session.commit()
except:
    session.rollback()
    raise
finally:
    session.close()
```

## 2. ORM Models

### Model Mapping

All domain models are mapped to database tables using SQLAlchemy's declarative base:

| Domain Model | ORM Model | Table Name |
|--------------|-----------|------------|
| User | `User` | `users` |
| Theme | `Theme` | `themes` |
| ThemedWorld | `ThemedWorld` | `themed_worlds` |
| Drawing | `Drawing` | `drawings` |
| AnimationData | `AnimationData` | `animation_data` |
| DrawingEntity | `DrawingEntity` | `drawing_entities` |
| ProcessingJob | `ProcessingJob` | `processing_jobs` |
| Notification | `Notification` | `notifications` |
| SystemLog | `SystemLog` | `system_logs` |

### Relationships

The ORM models include bidirectional relationships:

```python
# User -> Drawings (one-to-many)
user.drawings  # Access all drawings for a user

# Theme -> ThemedWorlds (one-to-many)
theme.themed_worlds  # Access all worlds for a theme

# ThemedWorld -> DrawingEntities (one-to-many)
world.drawing_entities  # Access all entities in a world

# Drawing -> AnimationData (one-to-one)
drawing.animation_data  # Access animation data for a drawing

# Drawing -> DrawingEntities (one-to-many)
drawing.drawing_entities  # Access all entity placements for a drawing

# Drawing -> ProcessingJobs (one-to-many)
drawing.processing_jobs  # Access all jobs for a drawing
```

### Key Features

- **UUID Primary Keys**: All models use UUID for primary keys
- **Automatic Timestamps**: `created_at` fields default to current timestamp
- **JSON Support**: Complex data stored as JSONB (positioning_rules, skeleton_data, etc.)
- **Indexes**: Performance indexes on frequently queried fields
- **Cascading Deletes**: Proper cascade rules for referential integrity

### Example Usage

```python
from database.orm import User, Theme, ThemedWorld, get_session
from uuid import uuid4
from datetime import datetime

session = get_session()

# Create a user
user = User(
    id=uuid4(),
    email='user@example.com',
    created_at=datetime.now(),
    total_drawings=0
)
session.add(user)

# Create a theme
theme = Theme(
    id=uuid4(),
    name='jungle',
    display_name='Jungle Adventure',
    background_image_url='/static/bg/jungle.jpg',
    dimensions_width=1920,
    dimensions_height=1080,
    max_entities=50,
    positioning_rules={'type': 'ground_based'},
    motion_sequences=['walk', 'run', 'climb']
)
session.add(theme)

# Create a world
world = ThemedWorld(
    id=uuid4(),
    theme_id=theme.id,
    instance_number=1,
    entity_count=0,
    is_full=False
)
session.add(world)

session.commit()
session.close()
```

## 3. Repository Pattern

### Purpose

The repository pattern provides a clean abstraction layer for data access, hiding the complexity of ORM operations and providing a consistent interface for CRUD operations.

### Base Repository

All repositories inherit from `BaseRepository[T]` which provides:

- `create(entity)` - Create a new entity
- `get_by_id(id)` - Retrieve entity by ID
- `get_all()` - Retrieve all entities
- `find_by(filters)` - Find entities matching filters
- `find_one_by(filters)` - Find single entity matching filters
- `update(id, updates)` - Update entity fields
- `delete(id)` - Delete entity by ID
- `count(filters)` - Count entities matching filters

### Specialized Repositories

Each domain model has a specialized repository with domain-specific methods:

#### UserRepository

```python
from database.repository import user_repository

# Get user by email
user = user_repository.get_by_email('user@example.com')

# Increment drawing count
user_repository.increment_drawing_count(user.id)
```

#### ThemeRepository

```python
from database.repository import theme_repository

# Get theme by name
theme = theme_repository.get_by_name('jungle')
```

#### ThemedWorldRepository

```python
from database.repository import themed_world_repository

# Get all worlds for a theme
worlds = themed_world_repository.get_by_theme(theme_id)

# Get first available (not full) world
world = themed_world_repository.get_available_world(theme_id)

# Increment entity count
themed_world_repository.increment_entity_count(world_id)
```

#### DrawingRepository

```python
from database.repository import drawing_repository

# Get all drawings for a user
drawings = drawing_repository.get_by_user(user_id)

# Get drawings by theme
drawings = drawing_repository.get_by_theme(theme_id)

# Get drawings by status
pending = drawing_repository.get_by_status('pending')
```

#### DrawingEntityRepository

```python
from database.repository import drawing_entity_repository

# Get all entities in a world (Requirement 9.2)
entities = drawing_entity_repository.get_by_world(world_id)

# Get all placements for a drawing
entities = drawing_entity_repository.get_by_drawing(drawing_id)
```

#### ProcessingJobRepository

```python
from database.repository import processing_job_repository

# Get jobs by status
queued = processing_job_repository.get_by_status('queued')

# Get queued jobs ordered by priority
jobs = processing_job_repository.get_queued_jobs()
```

### Session Management

Repositories support both automatic and manual session management:

```python
# Automatic session management (recommended)
user = user_repository.create(user_entity)

# Manual session management (for transactions)
session = get_session()
try:
    user = user_repository.create(user_entity, session)
    drawing = drawing_repository.create(drawing_entity, session)
    session.commit()
except:
    session.rollback()
    raise
finally:
    session.close()
```

## Requirement 9.2 Implementation

**Requirement 9.2:** THE Server SHALL maintain a database of all Themed_World instances and their associated Drawing_Entity instances

### Implementation

The ORM layer and repository pattern fully satisfy this requirement:

1. **ThemedWorld Persistence**: All themed world instances are stored in the `themed_worlds` table with complete metadata
2. **DrawingEntity Persistence**: All drawing entities are stored in the `drawing_entities` table with spatial coordinates and dimensions
3. **Relationship Maintenance**: Foreign key relationships ensure data integrity between worlds and entities
4. **Efficient Retrieval**: Indexed queries allow fast retrieval of all entities for a given world

### Example: Retrieving World with Entities

```python
from database.repository import themed_world_repository, drawing_entity_repository

# Get a themed world
world = themed_world_repository.get_by_id(world_id)

# Get all entities in the world
entities = drawing_entity_repository.get_by_world(world.id)

print(f"World {world.id} contains {len(entities)} entities:")
for entity in entities:
    print(f"  - Entity at ({entity.position_x}, {entity.position_y})")
```

### Example: Querying by Theme

```python
from database.repository import themed_world_repository, drawing_entity_repository

# Get all worlds for a theme
worlds = themed_world_repository.get_by_theme(theme_id)

# Get all entities across all worlds for this theme
all_entities = []
for world in worlds:
    entities = drawing_entity_repository.get_by_world(world.id)
    all_entities.extend(entities)

print(f"Theme has {len(worlds)} worlds with {len(all_entities)} total entities")
```

## Performance Considerations

### Connection Pooling

- **Pool Size**: Default 10 connections, configurable based on load
- **Max Overflow**: Additional 20 connections during peak load
- **Pre-ping**: Verifies connection health before use
- **Recycling**: Connections recycled after 1 hour to prevent stale connections

### Indexes

The following indexes optimize common queries:

- `idx_themed_worlds_theme_id` - Fast lookup of worlds by theme
- `idx_themed_worlds_is_full` - Fast lookup of available worlds
- `idx_drawing_entities_world_id` - Fast lookup of entities by world
- `idx_drawing_entities_drawing_id` - Fast lookup of entity placements
- `idx_drawings_user_id` - Fast lookup of drawings by user
- `idx_drawings_status` - Fast lookup of drawings by status
- `idx_processing_jobs_status` - Fast lookup of jobs by status

### Query Optimization

- Use `find_by()` with specific filters instead of `get_all()` + filtering
- Use `count()` instead of `len(get_all())` for counting
- Reuse sessions for multiple operations in a transaction
- Use eager loading for relationships when needed

## Error Handling

### Connection Errors

```python
from sqlalchemy.exc import OperationalError

try:
    session = get_session()
    # ... operations ...
except OperationalError as e:
    logger.error(f"Database connection error: {e}")
    # Retry logic or fallback
```

### Transaction Errors

```python
from sqlalchemy.exc import IntegrityError

try:
    user_repository.create(user)
except IntegrityError as e:
    logger.error(f"Constraint violation: {e}")
    # Handle duplicate email, etc.
```

## Testing

### Unit Tests

Test ORM models and repositories without a database using mocks:

```python
from unittest.mock import Mock, patch

def test_user_repository():
    with patch('database.repository.get_session') as mock_session:
        # Test repository methods
        pass
```

### Integration Tests

Test with a real database (see `test_orm_integration.py`):

```python
# Initialize test database
init_db('postgresql://localhost/test_db')

# Run tests
test_orm_mappings()
test_repository_pattern()
test_requirement_9_2()
```

## Migration

### Initial Setup

```bash
# Run migration script
python database/migrate.py
```

### Schema Updates

For schema changes, create new migration files in `database/migrations/` and update the migration script.

## Summary

The ORM integration provides:

✓ **Connection Pooling**: Efficient database connection management  
✓ **ORM Mappings**: Complete SQLAlchemy models for all domain entities  
✓ **Repository Pattern**: Clean data access abstraction  
✓ **Requirement 9.2**: Full support for maintaining themed worlds and entities  
✓ **Performance**: Indexed queries and connection pooling  
✓ **Relationships**: Bidirectional ORM relationships for easy navigation  
✓ **Error Handling**: Proper transaction management and error handling  

The implementation is production-ready and supports all requirements for the Themed Animation Platform.
