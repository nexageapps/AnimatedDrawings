"""
Demo script for Image Processing Service.

Demonstrates the complete image processing pipeline using test images.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_processing_service import ImageProcessingService, ImageMetadata
from services.storage_service import LocalStorageService


def demo_image_processing():
    """Demonstrate image processing with test images."""
    print("=" * 70)
    print("Image Processing Service Demo")
    print("=" * 70)
    
    # Initialize service
    print("\n1. Initializing Image Processing Service...")
    storage = LocalStorageService(base_path="uploads")
    service = ImageProcessingService(storage_service=storage)
    print("   ✓ Service initialized")
    
    # Find test image
    test_image_path = "test_images/garlic.png"
    if not os.path.exists(test_image_path):
        print(f"\n   ✗ Test image not found: {test_image_path}")
        print("   Please ensure test_images/garlic.png exists")
        return
    
    print(f"\n2. Validating test image: {test_image_path}")
    result = service.validate_image(test_image_path)
    
    if result.is_valid:
        print(f"   ✓ Valid image")
        print(f"     - Format: {result.format}")
        print(f"     - Dimensions: {result.dimensions[0]}x{result.dimensions[1]}")
        print(f"     - Size: {result.size_bytes / 1024:.2f} KB")
    else:
        print(f"   ✗ Invalid image: {result.error_message}")
        return
    
    # Process image
    print("\n3. Processing image (complete pipeline)...")
    metadata = ImageMetadata(
        sender_email="demo@example.com",
        theme_id="jungle",
        original_filename="garlic.png"
    )
    
    try:
        original_url, normalized_url = service.process_image(test_image_path, metadata)
        print(f"   ✓ Processing complete")
        print(f"     - Original stored: {original_url}")
        print(f"     - Normalized stored: {normalized_url}")
    except Exception as e:
        print(f"   ✗ Processing failed: {e}")
        return
    
    # Verify stored files
    print("\n4. Verifying stored files...")
    if storage.exists(original_url):
        original_path = storage.retrieve(original_url)
        print(f"   ✓ Original image exists: {original_path}")
    else:
        print(f"   ✗ Original image not found")
    
    if storage.exists(normalized_url):
        normalized_path = storage.retrieve(normalized_url)
        print(f"   ✓ Normalized image exists: {normalized_path}")
        
        # Check normalized image properties
        from PIL import Image
        with Image.open(normalized_path) as img:
            print(f"     - Format: {img.format}")
            print(f"     - Dimensions: {img.size[0]}x{img.size[1]}")
            print(f"     - Mode: {img.mode}")
    else:
        print(f"   ✗ Normalized image not found")
    
    # Test validation with different scenarios
    print("\n5. Testing validation scenarios...")
    
    # Test with nonexistent file
    result = service.validate_image("nonexistent.png")
    if not result.is_valid:
        print(f"   ✓ Correctly rejects nonexistent file")
    
    # Test unique identifier generation
    print("\n6. Testing unique identifier generation...")
    id1 = service.generate_unique_identifier()
    id2 = service.generate_unique_identifier()
    if id1 != id2:
        print(f"   ✓ Generates unique identifiers")
        print(f"     - ID 1: {id1}")
        print(f"     - ID 2: {id2}")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nThe Image Processing Service is ready for integration.")
    print("\nNext steps:")
    print("  - Integrate with Email Receiver Service (Task 7)")
    print("  - Integrate with API endpoints (Task 12)")
    print("  - Connect to Animation Engine Service (Task 4)")


if __name__ == "__main__":
    demo_image_processing()
