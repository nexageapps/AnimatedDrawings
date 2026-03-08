"""
Processing job domain model.

Represents a background processing job in the queue.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class JobStatus(Enum):
    """Status of a processing job."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingJob:
    """
    ProcessingJob model representing a background job.
    
    Jobs are queued for asynchronous processing of drawings through
    various stages (image processing, animation, composition).
    
    Attributes:
        id: Unique identifier (UUID)
        drawing_id: ID of the drawing being processed
        job_type: Type of job (image_processing, animation, composition)
        status: Current job status
        priority: Job priority (higher values processed first)
        attempts: Number of processing attempts made
        max_attempts: Maximum number of attempts before permanent failure
        error_message: Error details if job failed
        created_at: Timestamp when job was created
        started_at: Timestamp when job processing started
        completed_at: Timestamp when job completed (success or failure)
    """
    id: str
    drawing_id: str
    job_type: str
    status: JobStatus
    priority: int
    attempts: int
    max_attempts: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Valid job types
    VALID_JOB_TYPES = {'image_processing', 'animation', 'composition'}
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate the processing job model.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate job_type
        if self.job_type not in self.VALID_JOB_TYPES:
            return False, f"job_type must be one of {self.VALID_JOB_TYPES}, got {self.job_type}"
        
        # Validate status is a valid JobStatus
        if not isinstance(self.status, JobStatus):
            return False, f"status must be a JobStatus enum, got {type(self.status)}"
        
        # Validate attempts is non-negative
        if self.attempts < 0:
            return False, f"attempts must be non-negative, got {self.attempts}"
        
        # Validate max_attempts is positive
        if self.max_attempts <= 0:
            return False, f"max_attempts must be positive, got {self.max_attempts}"
        
        # Validate attempts doesn't exceed max_attempts
        if self.attempts > self.max_attempts:
            return False, f"attempts ({self.attempts}) cannot exceed max_attempts ({self.max_attempts})"
        
        # Validate timestamp ordering
        if self.started_at and self.started_at < self.created_at:
            return False, "started_at cannot be before created_at"
        
        if self.completed_at:
            if self.completed_at < self.created_at:
                return False, "completed_at cannot be before created_at"
            if self.started_at and self.completed_at < self.started_at:
                return False, "completed_at cannot be before started_at"
        
        # Validate error_message exists for failed jobs
        if self.status == JobStatus.FAILED and not self.error_message:
            return False, "error_message is required for failed jobs"
        
        return True, ""
    
    def __post_init__(self):
        """Validate on initialization and convert status string to enum if needed."""
        # Convert string status to enum if necessary
        if isinstance(self.status, str):
            try:
                self.status = JobStatus(self.status)
            except ValueError:
                raise ValueError(f"Invalid status value: {self.status}")
        
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(error)
    
    def is_complete(self) -> bool:
        """Check if job is complete (success or failure)."""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED)
    
    def is_successful(self) -> bool:
        """Check if job completed successfully."""
        return self.status == JobStatus.COMPLETED
    
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.status == JobStatus.FAILED and self.attempts < self.max_attempts
    
    def should_retry(self) -> bool:
        """Check if job should be retried (failed but hasn't exceeded max attempts)."""
        return self.status == JobStatus.FAILED and self.attempts < self.max_attempts
    
    def get_processing_duration(self) -> Optional[float]:
        """
        Get the processing duration in seconds.
        
        Returns:
            Duration in seconds if job has started, None otherwise
        """
        if not self.started_at:
            return None
        
        end_time = self.completed_at if self.completed_at else datetime.now()
        duration = (end_time - self.started_at).total_seconds()
        return duration
