"""
Unit tests for Image Processing Service and Storage Service.

Tests image validation, normalization, storage operations, and the complete
processing pipeline.
"""

import os
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import pytest

from services import (
    ImageProcessingService,
    StorageService,
    LocalStorageService,
    ValidationResult,
    ImageMetadata
)


class TestLocalStorageService:
    """Tests for LocalStorageService."""
    
    def setup_method(self):
        """Create temporary storage directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalStorageService(base_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary storage directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_storage_directories_created(self):
        """Test that storage service creates necessary directories."""
        assert (Path(self.temp_dir) / "original").exists()
        assert (Path(self.temp_dir) / "normalized").exists()
        assert (Path(self.temp_dir) / "animations").exists()
        assert (Path(self.temp_dir) / "masks").exists()
    
    def test_store_and_retrieve_file(self):
        """Test storing and retrieving a file."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        # Store the file
        identifier = self.storage.store(test_file, "original/test.txt")
        
        # Retrieve the file
        retrieved_path = self.storage.retrieve(identifier)
        
        # Verify content
        with open(retrieved_path, "r") as f:
            content = f.read()
        
        assert content == "test content"
    
    def test_store_generates_identifier(self):
        """Test that store generates UUID identifier if not provided."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "w") as f:
            f.write("test")
        
        # Store without identifier
        identifier = self.storage.store(test_file)
        
        # Should be in original directory with UUID name
        assert identifier.startswith("original/")
        assert identifier.endswith(".png")
    
    def test_exists(self):
        """Test checking if file exists."""
        # Create and store a file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        
        identifier = self.storage.store(test_file, "original/test.txt")
        
        # Check existence
        assert self.storage.exists(identifier) is True
        assert self.storage.exists("nonexistent/file.txt") is False
    
    def test_delete(self):
        """Test deleting a stored file."""
        # Create and store a file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        
        identifier = self.storage.store(test_file, "original/test.txt")
        
        # Delete the file
        result = self.storage.delete(identifier)
        
        assert result is True
        assert self.storage.exists(identifier) is False
    
    def test_store_nonexistent_file_raises_error(self):
        """Test that storing nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            self.storage.store("/nonexistent/file.txt")
    
    def test_retrieve_nonexistent_file_raises_error(self):
        """Test that retrieving nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            self.storage.retrieve("nonexistent/file.txt")


class TestImageProcessingService:
    """Tests for ImageProcessingService."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalStorageService(base_path=self.temp_dir)
        self.service = ImageProcessingService(storage_service=self.storage)
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, filename: str, size: tuple = (100, 100), 
                         format: str = "PNG") -> str:
        """Helper to create a test image."""
        path = os.path.join(self.temp_dir, filename)
        img = Image.new('RGB', size, color='red')
        img.save(path, format)
        return path
    
    def test_validate_valid_png(self):
        """Test validation of valid PNG image."""
        img_path = self.create_test_image("test.png", format="PNG")
        result = self.service.validate_image(img_path)
        
        assert result.is_valid is True
        assert result.format == "PNG"
        assert result.dimensions == (100, 100)
        assert result.error_message is None
    
    def test_validate_valid_jpeg(self):
        """Test validation of valid JPEG image."""
        img_path = self.create_test_image("test.jpg", format="JPEG")
        result = self.service.validate_image(img_path)
        
        assert result.is_valid is True
        assert result.format == "JPEG"
    
    def test_validate_valid_gif(self):
        """Test validation of valid GIF image."""
        img_path = self.create_test_image("test.gif", format="GIF")
        result = self.service.validate_image(img_path)
        
        assert result.is_valid is True
        assert result.format == "GIF"
    
    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        result = self.service.validate_image("/nonexistent/file.png")
        
        assert result.is_valid is False
        assert "not found" in result.error_message.lower()
    
    def test_validate_oversized_image(self):
        """Test validation rejects images over 10MB."""
        # Create a large image (will be over 10MB when saved)
        img_path = os.path.join(self.temp_dir, "large.png")
        # Create 4000x4000 image (should be > 10MB uncompressed)
        img = Image.new('RGB', (4000, 4000))
        img.save(img_path, "PNG", compress_level=0)
        
        # Check if file is actually over 10MB
        file_size = os.path.getsize(img_path)
        if file_size > 10 * 1024 * 1024:
            result = self.service.validate_image(img_path)
            assert result.is_valid is False
            assert "too large" in result.error_message.lower()
    
    def test_validate_corrupted_image(self):
        """Test validation detects corrupted images."""
        # Create a corrupted image file
        corrupted_path = os.path.join(self.temp_dir, "corrupted.png")
        with open(corrupted_path, "wb") as f:
            f.write(b"not a real image file")
        
        result = self.service.validate_image(corrupted_path)
        
        assert result.is_valid is False
        assert "corrupted" in result.error_message.lower() or "invalid" in result.error_message.lower()
    
    def test_normalize_image_resizes_large_image(self):
        """Test normalization resizes images larger than 2048x2048."""
        # Create large image
        img_path = self.create_test_image("large.png", size=(3000, 3000))
        
        # Normalize
        normalized_path = self.service.normalize_image(img_path)
        
        # Check dimensions
        with Image.open(normalized_path) as img:
            assert img.width <= 2048
            assert img.height <= 2048
            assert img.format == "PNG"
        
        # Clean up
        os.remove(normalized_path)
    
    def test_normalize_image_maintains_aspect_ratio(self):
        """Test normalization maintains aspect ratio."""
        # Create rectangular image
        img_path = self.create_test_image("rect.png", size=(3000, 1500))
        
        # Normalize
        normalized_path = self.service.normalize_image(img_path)
        
        # Check aspect ratio maintained
        with Image.open(normalized_path) as img:
            aspect_ratio = img.width / img.height
            assert abs(aspect_ratio - 2.0) < 0.01  # Should be ~2:1
        
        # Clean up
        os.remove(normalized_path)
    
    def test_normalize_image_converts_to_png(self):
        """Test normalization converts images to PNG."""
        # Create JPEG image
        img_path = self.create_test_image("test.jpg", format="JPEG")
        
        # Normalize
        normalized_path = self.service.normalize_image(img_path)
        
        # Check format
        with Image.open(normalized_path) as img:
            assert img.format == "PNG"
        
        # Clean up
        os.remove(normalized_path)
    
    def test_normalize_small_image_unchanged(self):
        """Test normalization doesn't resize small images."""
        # Create small image
        img_path = self.create_test_image("small.png", size=(500, 500))
        
        # Normalize
        normalized_path = self.service.normalize_image(img_path)
        
        # Check dimensions unchanged
        with Image.open(normalized_path) as img:
            assert img.size == (500, 500)
        
        # Clean up
        os.remove(normalized_path)
    
    def test_generate_unique_identifier(self):
        """Test unique identifier generation."""
        id1 = self.service.generate_unique_identifier()
        id2 = self.service.generate_unique_identifier()
        
        # Should be different
        assert id1 != id2
        # Should have .png extension
        assert id1.endswith(".png")
        assert id2.endswith(".png")
    
    def test_store_image(self):
        """Test storing an image."""
        img_path = self.create_test_image("test.png")
        
        # Store image
        stored_url = self.service.store_image(img_path, "original")
        
        # Verify stored
        assert stored_url.startswith("original/")
        assert self.storage.exists(stored_url)
    
    def test_process_image_complete_pipeline(self):
        """Test complete image processing pipeline."""
        # Create test image
        img_path = self.create_test_image("test.png", size=(1000, 1000))
        
        # Create metadata
        metadata = ImageMetadata(
            sender_email="test@example.com",
            theme_id="jungle",
            original_filename="test.png"
        )
        
        # Process image
        original_url, normalized_url = self.service.process_image(img_path, metadata)
        
        # Verify both images stored
        assert self.storage.exists(original_url)
        assert self.storage.exists(normalized_url)
        
        # Verify normalized image is PNG
        normalized_path = self.storage.retrieve(normalized_url)
        with Image.open(normalized_path) as img:
            assert img.format == "PNG"
    
    def test_process_image_rejects_invalid(self):
        """Test processing rejects invalid images."""
        # Create corrupted image
        corrupted_path = os.path.join(self.temp_dir, "corrupted.png")
        with open(corrupted_path, "wb") as f:
            f.write(b"not an image")
        
        metadata = ImageMetadata(
            sender_email="test@example.com",
            theme_id="jungle"
        )
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            self.service.process_image(corrupted_path, metadata)
        
        assert "validation failed" in str(exc_info.value).lower()


def run_tests():
    """Run all tests."""
    print("Running Image Processing Service Tests...")
    print("=" * 60)
    
    # Test LocalStorageService
    print("\n1. Testing LocalStorageService...")
    test_storage = TestLocalStorageService()
    
    test_storage.setup_method()
    test_storage.test_storage_directories_created()
    print("   ✓ Storage directories created")
    test_storage.teardown_method()
    
    test_storage.setup_method()
    test_storage.test_store_and_retrieve_file()
    print("   ✓ Store and retrieve file")
    test_storage.teardown_method()
    
    test_storage.setup_method()
    test_storage.test_exists()
    print("   ✓ File existence check")
    test_storage.teardown_method()
    
    test_storage.setup_method()
    test_storage.test_delete()
    print("   ✓ File deletion")
    test_storage.teardown_method()
    
    # Test ImageProcessingService
    print("\n2. Testing ImageProcessingService...")
    test_service = TestImageProcessingService()
    
    test_service.setup_method()
    test_service.test_validate_valid_png()
    print("   ✓ Validate PNG image")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_validate_valid_jpeg()
    print("   ✓ Validate JPEG image")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_validate_valid_gif()
    print("   ✓ Validate GIF image")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_validate_corrupted_image()
    print("   ✓ Detect corrupted image")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_normalize_image_resizes_large_image()
    print("   ✓ Normalize resizes large images")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_normalize_image_maintains_aspect_ratio()
    print("   ✓ Normalize maintains aspect ratio")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_normalize_image_converts_to_png()
    print("   ✓ Normalize converts to PNG")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_generate_unique_identifier()
    print("   ✓ Generate unique identifiers")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_process_image_complete_pipeline()
    print("   ✓ Complete processing pipeline")
    test_service.teardown_method()
    
    test_service.setup_method()
    test_service.test_process_image_rejects_invalid()
    print("   ✓ Reject invalid images")
    test_service.teardown_method()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("\nImage Processing Service is ready for integration.")


if __name__ == "__main__":
    run_tests()
