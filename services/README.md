# Services Layer

This directory contains business logic services that orchestrate operations across models, database access, and external systems.

## Overview

Services implement the core business logic of the Themed Animation Platform. They:
- Coordinate operations across multiple components
- Enforce business rules and validation
- Provide clean interfaces for controllers/API endpoints
- Handle error conditions and logging

## Available Services

### ThemeManagerService

Manages theme operations including CRUD, validation, and theme-to-motion-sequence mapping.

**Requirements**: 4.1, 4.2, 4.3, 4.4, 4.5, 11.5

**Key Features**:
- Theme CRUD operations (Create, Read, Update, Delete)
- Theme validation
- Default theme logic
- Theme-to-motion-sequence mapping
- Theme property retrieval

**Usage Example**:

```python
from services import ThemeManagerService

# Initialize service
theme_service = ThemeManagerService()

# Get a theme
jungle_theme = theme_service.get_theme('jungle')
print(f"Theme: {jungle_theme.display_name}")
print(f"Dimensions: {jungle_theme.dimensions}")

# Validate theme exists
is_valid = theme_service.validate_theme('christmas')
print(f"Christmas theme exists: {is_valid}")

# Get default theme
default_theme = theme_service.get_default_theme()
print(f"Default theme: {default_theme.name}")

# Get motion sequences for a theme
motions = theme_service.get_motion_sequences_for_theme('party')
print(f"Party motions: {motions}")

# Get all themes
all_themes = theme_service.get_all_themes()
for theme in all_themes:
    print(f"- {theme.name}: {theme.display_name}")
```

**Methods**:

- `get_theme(theme_name: str) -> Optional[Theme]`
  - Retrieve theme by name
  
- `get_theme_by_id(theme_id: str) -> Optional[Theme]`
  - Retrieve theme by UUID
  
- `get_all_themes() -> List[Theme]`
  - Get all available themes
  
- `validate_theme(theme_name: str) -> bool`
  - Check if theme exists
  
- `get_default_theme() -> Theme`
  - Get the default theme (general)
  
- `get_theme_properties(theme_name: str) -> Optional[Dict]`
  - Get complete theme properties
  
- `get_motion_sequences_for_theme(theme_name: str) -> List[str]`
  - Get motion sequences for a theme
  
- `create_theme(theme: Theme) -> bool`
  - Create a new theme
  
- `update_theme(theme: Theme) -> bool`
  - Update existing theme
  
- `delete_theme(theme_name: str) -> bool`
  - Delete a theme (cannot delete default theme)

**Theme-Motion Mapping**:

The service maintains a mapping of themes to appropriate motion sequences:

```python
THEME_MOTIONS = {
    'jungle': ['zombie', 'jumping', 'wave_hello'],
    'christmas': ['jesse_dance', 'wave_hello', 'dab'],
    'party': ['jesse_dance', 'jumping', 'dab', 'jumping_jacks'],
    'school': ['wave_hello', 'jumping', 'dab'],
    'ocean': ['wave_hello', 'zombie', 'jesse_dance'],
    'general': ['wave_hello', 'jumping', 'dab']
}
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API / Controllers                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Services Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ThemeManagerService                             │  │
│  │  - CRUD operations                               │  │
│  │  - Validation logic                              │  │
│  │  - Business rules                                │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Database / ORM Layer                       │
│  - SQLAlchemy ORM models                                │
│  - Database connections                                 │
│  - Query execution                                      │
└─────────────────────────────────────────────────────────┘
```

## Testing

Each service should have corresponding tests:

```bash
# Run service tests
python3 services/test_theme_manager.py
```

## Future Services

The following services will be added as the platform develops:

- **ImageProcessingService**: Image validation, normalization, and storage
- **AnimationEngineService**: Facebook Animated Drawings integration
- **WorldCompositorService**: Spatial positioning and world management
- **RenderingService**: Scene composition and video generation
- **NotificationService**: Email notifications and alerts
- **EmailReceiverService**: Email monitoring and parsing

## Design Principles

1. **Single Responsibility**: Each service has a clear, focused purpose
2. **Dependency Injection**: Services receive dependencies rather than creating them
3. **Error Handling**: Services catch and log errors, returning appropriate values
4. **Testability**: Services are designed to be easily testable
5. **Separation of Concerns**: Business logic is separate from data access and presentation

## Error Handling

Services follow consistent error handling patterns:

```python
def some_operation(self, param: str) -> Optional[Result]:
    """
    Perform some operation.
    
    Returns:
        Result object if successful, None if failed
    """
    session = get_session()
    try:
        # Perform operation
        result = do_something(param)
        session.commit()
        logger.info(f"Operation successful: {param}")
        return result
    except Exception as e:
        session.rollback()
        logger.error(f"Operation failed for {param}: {e}")
        return None
    finally:
        session.close()
```

## Logging

Services use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for unexpected situations")
logger.error("Error messages for failures")
logger.critical("Critical errors that may cause system failure")
```

## Configuration

Services may require configuration from:
- Environment variables
- Configuration files
- Database settings

Example:
```python
import os

class SomeService:
    def __init__(self):
        self.api_key = os.environ.get('API_KEY')
        self.timeout = int(os.environ.get('TIMEOUT', '30'))
```

## Contributing

When adding new services:

1. Create a new file in this directory (e.g., `my_service.py`)
2. Implement the service class with clear docstrings
3. Add the service to `__init__.py`
4. Create corresponding tests
5. Update this README with service documentation
6. Map service methods to requirements in docstrings
