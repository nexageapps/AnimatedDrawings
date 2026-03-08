"""
User domain model.

Represents a user in the system, identified by email address.
"""

from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class User:
    """
    User model representing a platform user.
    
    Users are identified by their email address and can submit multiple drawings.
    
    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (must be valid format)
        created_at: Timestamp when user was created
        total_drawings: Count of drawings submitted by this user
    """
    id: str
    email: str
    created_at: datetime
    total_drawings: int
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the user model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate email format
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(email_pattern, self.email):
            return False, f"Invalid email format: {self.email}"
        
        # Validate total_drawings is non-negative
        if self.total_drawings < 0:
            return False, f"total_drawings must be non-negative, got {self.total_drawings}"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization."""
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
