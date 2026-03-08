"""
Theme domain model.

Represents a themed environment with its properties and rules.
"""

from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class Theme:
    """
    Theme model representing a themed environment.
    
    Themes define the visual and behavioral properties of worlds where
    animated drawings are placed.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Internal theme name (e.g., 'jungle', 'christmas')
        display_name: Human-readable theme name
        background_image_url: URL/path to the theme's background image
        dimensions: Tuple of (width, height) in pixels
        max_entities: Maximum number of entities allowed in a world of this theme
        positioning_rules: Dictionary containing positioning algorithm rules
        motion_sequences: List of motion sequence names available for this theme
    """
    id: str
    name: str
    display_name: str
    background_image_url: str
    dimensions: Tuple[int, int]
    max_entities: int
    positioning_rules: dict
    motion_sequences: List[str]
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the theme model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate name is not empty
        if not self.name or not self.name.strip():
            return False, "name cannot be empty"
        
        # Validate display_name is not empty
        if not self.display_name or not self.display_name.strip():
            return False, "display_name cannot be empty"
        
        # Validate dimensions are positive
        width, height = self.dimensions
        if width <= 0 or height <= 0:
            return False, f"dimensions must be positive, got ({width}, {height})"
        
        # Validate max_entities is positive
        if self.max_entities <= 0:
            return False, f"max_entities must be positive, got {self.max_entities}"
        
        # Validate positioning_rules is a dict
        if not isinstance(self.positioning_rules, dict):
            return False, f"positioning_rules must be a dict, got {type(self.positioning_rules)}"
        
        # Validate motion_sequences is a list
        if not isinstance(self.motion_sequences, list):
            return False, f"motion_sequences must be a list, got {type(self.motion_sequences)}"
        
        # Validate motion_sequences is not empty
        if not self.motion_sequences:
            return False, "motion_sequences cannot be empty"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization."""
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
    
    @property
    def width(self) -> int:
        """Get theme width."""
        return self.dimensions[0]
    
    @property
    def height(self) -> int:
        """Get theme height."""
        return self.dimensions[1]
    
    def has_motion_sequence(self, motion: str) -> bool:
        """Check if theme supports a specific motion sequence."""
        return motion in self.motion_sequences
