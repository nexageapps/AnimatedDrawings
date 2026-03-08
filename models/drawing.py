"""
Drawing domain model.

Represents a drawing submission with its processing status.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DrawingStatus(Enum):
    """Status of a drawing in the processing pipeline."""
    PENDING = "pending"
    PROCESSING = "processing"
    ANIMATED = "animated"
    FAILED = "failed"


@dataclass
class Drawing:
    """
    Drawing model representing a user's submitted drawing.
    
    Tracks the drawing through the processing pipeline from submission
    to animation completion.
    
    Attributes:
        id: Unique identifier (UUID)
        user_id: ID of the user who submitted the drawing
        original_image_url: URL/path to the original uploaded image
        normalized_image_url: URL/path to the normalized/processed image
        status: Current processing status
        theme_id: ID of the theme assigned to this drawing
        created_at: Timestamp when drawing was submitted
        processed_at: Timestamp when processing completed (if applicable)
        error_message: Error details if processing failed
    """
    id: str
    user_id: str
    original_image_url: str
    normalized_image_url: Optional[str]
    status: DrawingStatus
    theme_id: str
    created_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the drawing model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate original_image_url is not empty
        if not self.original_image_url or not self.original_image_url.strip():
            return False, "original_image_url cannot be empty"
        
        # Validate status is a valid DrawingStatus
        if not isinstance(self.status, DrawingStatus):
            return False, f"status must be a DrawingStatus enum, got {type(self.status)}"
        
        # Validate processed_at is after created_at if both exist
        if self.processed_at and self.processed_at < self.created_at:
            return False, "processed_at cannot be before created_at"
        
        # Validate error_message exists only for failed status
        if self.status == DrawingStatus.FAILED and not self.error_message:
            return False, "error_message is required for failed drawings"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization and convert status string to enum if needed."""
        # Convert string status to enum if necessary
        if isinstance(self.status, str):
            try:
                self.status = DrawingStatus(self.status)
            except ValueError:
                raise ValueError(f"Invalid status value: {self.status}")
        
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
    
    def is_complete(self) -> bool:
        """Check if drawing processing is complete (success or failure)."""
        return self.status in (DrawingStatus.ANIMATED, DrawingStatus.FAILED)
    
    def is_successful(self) -> bool:
        """Check if drawing was successfully animated."""
        return self.status == DrawingStatus.ANIMATED
