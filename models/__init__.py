"""
Domain models for the Themed Animation Platform.

This module contains the core domain models that represent the business entities
in the system. These models match the database schema and include validation logic.

Requirements: 2.2, 9.1
"""

from .user import User
from .theme import Theme
from .themed_world import ThemedWorld
from .drawing import Drawing, DrawingStatus
from .animation_data import AnimationData
from .drawing_entity import DrawingEntity
from .processing_job import ProcessingJob, JobStatus

__all__ = [
    'User',
    'Theme',
    'ThemedWorld',
    'Drawing',
    'DrawingStatus',
    'AnimationData',
    'DrawingEntity',
    'ProcessingJob',
    'JobStatus',
]
