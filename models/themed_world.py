"""
Themed world domain model.

Represents an instance of a themed world where drawings are placed.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ThemedWorld:
    """
    ThemedWorld model representing a world instance.
    
    Multiple instances of the same theme can exist when worlds reach capacity.
    Each world contains multiple drawing entities positioned spatially.
    
    Attributes:
        id: Unique identifier (UUID)
        theme_id: ID of the theme this world belongs to
        instance_number: Instance number for this theme (1, 2, 3, ...)
        entity_count: Current number of entities in this world
        is_full: Whether this world has reached capacity
        created_at: Timestamp when world was created
        last_updated: Timestamp of last modification
    """
    id: str
    theme_id: str
    instance_number: int
    entity_count: int
    is_full: bool
    created_at: datetime
    last_updated: datetime
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the themed world model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate instance_number is positive
        if self.instance_number <= 0:
            return False, f"instance_number must be positive, got {self.instance_number}"
        
        # Validate entity_count is non-negative
        if self.entity_count < 0:
            return False, f"entity_count must be non-negative, got {self.entity_count}"
        
        # Validate last_updated is after or equal to created_at
        if self.last_updated < self.created_at:
            return False, "last_updated cannot be before created_at"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization."""
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
    
    def can_add_entity(self, max_entities: int) -> bool:
        """
        Check if this world can accept another entity.
        
        Args:
            max_entities: Maximum entities allowed (from theme)
            
        Returns:
            True if entity can be added, False otherwise
        """
        return not self.is_full and self.entity_count < max_entities
    
    def get_occupancy_rate(self, max_entities: int) -> float:
        """
        Calculate the occupancy rate of this world.
        
        Args:
            max_entities: Maximum entities allowed (from theme)
            
        Returns:
            Occupancy rate as a float between 0.0 and 1.0
        """
        if max_entities <= 0:
            return 0.0
        return min(self.entity_count / max_entities, 1.0)
