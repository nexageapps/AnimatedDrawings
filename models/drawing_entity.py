"""
Drawing entity domain model.

Represents a drawing placed within a themed world with spatial coordinates.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
import math


@dataclass
class DrawingEntity:
    """
    DrawingEntity model representing a drawing placed in a world.
    
    Entities have spatial coordinates and dimensions within a themed world.
    
    Attributes:
        id: Unique identifier (UUID)
        drawing_id: ID of the drawing this entity represents
        world_id: ID of the world this entity is placed in
        position: Tuple of (x, y) coordinates in pixels
        z_index: Z-order for layering (higher values appear in front)
        dimensions: Tuple of (width, height) in pixels
        created_at: Timestamp when entity was placed
    """
    id: str
    drawing_id: str
    world_id: str
    position: Tuple[int, int]
    z_index: int
    dimensions: Tuple[int, int]
    created_at: datetime
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the drawing entity model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate position is non-negative
        x, y = self.position
        if x < 0 or y < 0:
            return False, f"position must be non-negative, got ({x}, {y})"
        
        # Validate dimensions are positive
        width, height = self.dimensions
        if width <= 0 or height <= 0:
            return False, f"dimensions must be positive, got ({width}, {height})"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization."""
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
    
    @property
    def x(self) -> int:
        """Get x coordinate."""
        return self.position[0]
    
    @property
    def y(self) -> int:
        """Get y coordinate."""
        return self.position[1]
    
    @property
    def width(self) -> int:
        """Get entity width."""
        return self.dimensions[0]
    
    @property
    def height(self) -> int:
        """Get entity height."""
        return self.dimensions[1]
    
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """
        Get the bounding box of this entity.
        
        Returns:
            Tuple of (x1, y1, x2, y2) representing top-left and bottom-right corners
        """
        x1, y1 = self.position
        x2 = x1 + self.width
        y2 = y1 + self.height
        return (x1, y1, x2, y2)
    
    def get_center(self) -> Tuple[float, float]:
        """
        Get the center point of this entity.
        
        Returns:
            Tuple of (center_x, center_y)
        """
        x, y = self.position
        center_x = x + self.width / 2
        center_y = y + self.height / 2
        return (center_x, center_y)
    
    def distance_to(self, other: 'DrawingEntity') -> float:
        """
        Calculate the distance between this entity and another.
        
        Uses center-to-center Euclidean distance.
        
        Args:
            other: Another DrawingEntity
            
        Returns:
            Distance in pixels
        """
        x1, y1 = self.get_center()
        x2, y2 = other.get_center()
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def overlaps_with(self, other: 'DrawingEntity', min_spacing: int = 0) -> bool:
        """
        Check if this entity overlaps with another entity.
        
        Args:
            other: Another DrawingEntity
            min_spacing: Minimum spacing required between entities (default: 0)
            
        Returns:
            True if entities overlap (considering min_spacing), False otherwise
        """
        x1_min, y1_min, x1_max, y1_max = self.get_bounding_box()
        x2_min, y2_min, x2_max, y2_max = other.get_bounding_box()
        
        # Expand bounding boxes by min_spacing
        x1_min -= min_spacing
        y1_min -= min_spacing
        x1_max += min_spacing
        y1_max += min_spacing
        
        # Check for overlap
        return not (x1_max < x2_min or x2_max < x1_min or 
                   y1_max < y2_min or y2_max < y1_min)
