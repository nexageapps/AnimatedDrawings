"""
Animation data domain model.

Represents the animation processing results for a drawing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AnimationData:
    """
    AnimationData model representing animation processing results.
    
    Contains the outputs from the Facebook Animated Drawings library including
    character detection, segmentation, skeleton data, and animation files.
    
    Attributes:
        id: Unique identifier (UUID)
        drawing_id: ID of the drawing this animation belongs to
        character_detected: Whether a character was successfully detected
        segmentation_mask_url: URL/path to the segmentation mask image
        skeleton_data: Dictionary containing skeleton/joint data (JSONB)
        motion_sequence: Name of the motion sequence applied
        animation_file_url: URL/path to the animation output file
        sprite_sheet_url: URL/path to the sprite sheet (if generated)
    """
    id: str
    drawing_id: str
    character_detected: bool
    segmentation_mask_url: Optional[str]
    skeleton_data: Optional[dict]
    motion_sequence: Optional[str]
    animation_file_url: Optional[str]
    sprite_sheet_url: Optional[str]
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the animation data model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # If character was detected, certain fields should be present
        if self.character_detected:
            if not self.segmentation_mask_url:
                return False, "segmentation_mask_url required when character_detected is True"
            
            if not self.skeleton_data:
                return False, "skeleton_data required when character_detected is True"
            
            if not self.motion_sequence:
                return False, "motion_sequence required when character_detected is True"
            
            if not self.animation_file_url:
                return False, "animation_file_url required when character_detected is True"
        
        # Validate skeleton_data is a dict if present
        if self.skeleton_data is not None and not isinstance(self.skeleton_data, dict):
            return False, f"skeleton_data must be a dict, got {type(self.skeleton_data)}"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization."""
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
    
    def is_complete(self) -> bool:
        """Check if animation processing is complete."""
        return self.character_detected and self.animation_file_url is not None
    
    def has_sprite_sheet(self) -> bool:
        """Check if a sprite sheet was generated."""
        return self.sprite_sheet_url is not None
