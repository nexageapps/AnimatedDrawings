"""
Image Processing Service.

Handles image validation, normalization, and storage coordination.

Requirements: 2.1, 2.2, 2.5
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
from PIL import Image
import logging

from .storage_service import StorageService, LocalStorageService

logger = logging.getLogger(__name__)

# Constants from requirements
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
SUPPORTED_FORMATS = {'PNG', 'JPEG', 'JPG', 'GIF'}
MAX_DIMENSION = 2048


@dataclass
class ValidationResult:
    """Result of image validation."""
    is_valid: bool
    error_message: Optional[str] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None


@dataclass
class ImageMetadata:
    """Metadata for storing an image."""
    sender_email: str
    theme_id: str
    original_filename: Optional[str] = None


class ImageProcessingService:
    """
    Service for processing images in the themed animation platform.
    
    Handles:
    - Image validation (format, size, corruption)
    - Image normalization (resize, format conversion)
    - Storage coordination
    - Unique identifier generation
    
    Requirements: 2.1, 2.2, 2.5
    """
    
    def __init__(self, storage_service: Optional[StorageService] = None):
        """
        Initialize image processing service.
        
        Args:
            storage_service: Storage service to use (defaults to LocalStorageService)
        """
        self.storage_service = storage_service or LocalStorageService()
        logger.info("ImageProcessingService initialized")
    
    def validate_image(self, file_path: str) -> ValidationResult:
        """
        Validate image meets requirements.
        
        Checks:
        - File exists and is readable
        - Format is supported (PNG, JPG, JPEG, GIF)
        - Size is under 10MB
        - Image is not corrupted
        
        Args:
            file_path: Path to image file
            
        Returns:
            ValidationResult with validation status and details
            
        Requirements: 2.1, 2.5
        """
        # Check file exists
        if not os.path.exists(file_path):
            return ValidationResult(
                is_valid=False,
                error_message=f"File not found: {file_path}"
            )
        
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
        except OSError as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Cannot read file size: {e}"
            )
        
        if file_size > MAX_IMAGE_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            return ValidationResult(
                is_valid=False,
                error_message=f"Image too large: {size_mb:.2f}MB (max {MAX_IMAGE_SIZE_MB}MB)",
                size_bytes=file_size
            )
        
        # Try to open and validate image
        try:
            with Image.open(file_path) as img:
                # Check format
                img_format = img.format.upper() if img.format else None
                
                if img_format not in SUPPORTED_FORMATS:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Unsupported format: {img_format}. Supported: {', '.join(SUPPORTED_FORMATS)}",
                        format=img_format,
                        size_bytes=file_size
                    )
                
                # Verify image can be loaded (checks for corruption)
                img.verify()
                
                # Re-open to get dimensions (verify() closes the file)
                with Image.open(file_path) as img2:
                    dimensions = img2.size
                
                logger.info(f"Image validated: {file_path} - {img_format} {dimensions} ({file_size} bytes)")
                
                return ValidationResult(
                    is_valid=True,
                    format=img_format,
                    size_bytes=file_size,
                    dimensions=dimensions
                )
                
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Image corrupted or invalid: {e}",
                size_bytes=file_size
            )
    
    def normalize_image(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Normalize image for animation processing.
        
        Normalization:
        - Resize to max 2048x2048 (maintains aspect ratio)
        - Convert to PNG format
        - Ensure RGB mode
        
        Args:
            file_path: Path to source image
            output_path: Optional output path (generates temp file if not provided)
            
        Returns:
            Path to normalized image
            
        Raises:
            IOError: If normalization fails
            
        Requirements: 2.1
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                elif img.mode == 'RGBA':
                    # Create white background for RGBA images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    img = background
                
                # Resize if necessary (maintain aspect ratio)
                if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
                    logger.info(f"Resized image to {img.size}")
                
                # Generate output path if not provided
                if output_path is None:
                    output_path = f"/tmp/{uuid.uuid4()}.png"
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save as PNG
                img.save(output_path, 'PNG', optimize=True)
                logger.info(f"Normalized image saved: {output_path}")
                
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to normalize image {file_path}: {e}")
            raise IOError(f"Image normalization failed: {e}")
    
    def generate_unique_identifier(self, extension: str = ".png") -> str:
        """
        Generate unique identifier for an image.
        
        Args:
            extension: File extension (default: .png)
            
        Returns:
            Unique identifier string
            
        Requirements: 2.2
        """
        return f"{uuid.uuid4()}{extension}"
    
    def store_image(self, file_path: str, image_type: str = "original") -> str:
        """
        Store image in storage service.
        
        Args:
            file_path: Path to image file
            image_type: Type of image (original, normalized, etc.)
            
        Returns:
            Storage identifier/URL
            
        Raises:
            IOError: If storage fails
            
        Requirements: 2.2
        """
        # Generate unique identifier
        file_ext = Path(file_path).suffix or ".png"
        identifier = self.generate_unique_identifier(file_ext)
        
        # Add subdirectory based on type
        storage_path = f"{image_type}/{identifier}"
        
        # Store using storage service
        try:
            stored_path = self.storage_service.store(file_path, storage_path)
            logger.info(f"Stored {image_type} image: {stored_path}")
            return stored_path
        except Exception as e:
            logger.error(f"Failed to store image {file_path}: {e}")
            raise IOError(f"Image storage failed: {e}")
    
    def process_image(self, file_path: str, metadata: ImageMetadata) -> Tuple[str, str]:
        """
        Complete image processing pipeline.
        
        Steps:
        1. Validate image
        2. Store original image
        3. Normalize image
        4. Store normalized image
        
        Args:
            file_path: Path to uploaded image
            metadata: Image metadata (sender, theme, etc.)
            
        Returns:
            Tuple of (original_image_url, normalized_image_url)
            
        Raises:
            ValueError: If validation fails
            IOError: If processing or storage fails
            
        Requirements: 2.1, 2.2, 2.5
        """
        # Validate image
        validation = self.validate_image(file_path)
        if not validation.is_valid:
            logger.warning(f"Image validation failed: {validation.error_message}")
            raise ValueError(f"Image validation failed: {validation.error_message}")
        
        logger.info(f"Processing image for {metadata.sender_email}, theme: {metadata.theme_id}")
        
        # Store original image
        original_url = self.store_image(file_path, "original")
        
        # Normalize image
        normalized_path = self.normalize_image(file_path)
        
        try:
            # Store normalized image
            normalized_url = self.store_image(normalized_path, "normalized")
            
            logger.info(f"Image processing complete: original={original_url}, normalized={normalized_url}")
            
            return original_url, normalized_url
            
        finally:
            # Clean up temporary normalized file
            if normalized_path.startswith("/tmp/"):
                try:
                    os.remove(normalized_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {normalized_path}: {e}")
