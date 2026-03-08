"""
Storage Service abstraction layer.

Provides interface for storing and retrieving images with support for
different storage backends (local filesystem, S3, etc.).

Requirements: 2.2
"""

import os
import shutil
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """
    Abstract base class for storage services.
    
    Defines the interface that all storage implementations must follow.
    """
    
    @abstractmethod
    def store(self, file_path: str, identifier: Optional[str] = None) -> str:
        """
        Store a file and return its identifier/URL.
        
        Args:
            file_path: Path to the file to store
            identifier: Optional custom identifier (generates UUID if not provided)
            
        Returns:
            Storage identifier/URL for the stored file
            
        Raises:
            IOError: If storage operation fails
        """
        pass
    
    @abstractmethod
    def retrieve(self, identifier: str) -> str:
        """
        Retrieve the path to a stored file.
        
        Args:
            identifier: Storage identifier/URL
            
        Returns:
            Local path to the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """
        Delete a stored file.
        
        Args:
            identifier: Storage identifier/URL
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            identifier: Storage identifier/URL
            
        Returns:
            True if file exists, False otherwise
        """
        pass


class LocalStorageService(StorageService):
    """
    Local filesystem storage implementation.
    
    Stores files in a local directory structure organized by type
    (original, normalized, animations, etc.).
    
    Requirements: 2.2
    """
    
    def __init__(self, base_path: str = "uploads"):
        """
        Initialize local storage service.
        
        Args:
            base_path: Base directory for storing files
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary storage directories if they don't exist."""
        directories = [
            self.base_path / "original",
            self.base_path / "normalized",
            self.base_path / "animations",
            self.base_path / "masks",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def store(self, file_path: str, identifier: Optional[str] = None) -> str:
        """
        Store a file in local filesystem.
        
        Args:
            file_path: Path to the file to store
            identifier: Optional custom identifier (generates UUID if not provided)
            
        Returns:
            Storage path relative to base_path
            
        Raises:
            IOError: If file copy fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Generate identifier if not provided
        if identifier is None:
            file_ext = Path(file_path).suffix
            identifier = f"{uuid.uuid4()}{file_ext}"
        
        # Determine subdirectory based on file type
        # Default to 'original' if not specified in identifier
        if "/" in identifier:
            dest_path = self.base_path / identifier
        else:
            dest_path = self.base_path / "original" / identifier
        
        # Ensure parent directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy file to storage
            shutil.copy2(file_path, dest_path)
            logger.info(f"Stored file: {file_path} -> {dest_path}")
            
            # Return relative path from base_path
            return str(dest_path.relative_to(self.base_path))
        except Exception as e:
            logger.error(f"Failed to store file {file_path}: {e}")
            raise IOError(f"Storage operation failed: {e}")
    
    def retrieve(self, identifier: str) -> str:
        """
        Retrieve the full path to a stored file.
        
        Args:
            identifier: Storage identifier (relative path)
            
        Returns:
            Absolute path to the file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.base_path / identifier
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found in storage: {identifier}")
        
        return str(file_path.absolute())
    
    def delete(self, identifier: str) -> bool:
        """
        Delete a stored file.
        
        Args:
            identifier: Storage identifier (relative path)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = self.base_path / identifier
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {identifier}")
                return True
            else:
                logger.warning(f"File not found for deletion: {identifier}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {identifier}: {e}")
            return False
    
    def exists(self, identifier: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            identifier: Storage identifier (relative path)
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.base_path / identifier
        return file_path.exists()
    
    def get_full_path(self, identifier: str) -> str:
        """
        Get the full absolute path for an identifier.
        
        Args:
            identifier: Storage identifier (relative path)
            
        Returns:
            Absolute path to the file location
        """
        return str((self.base_path / identifier).absolute())
