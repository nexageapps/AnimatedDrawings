"""
Demo script for Animation Engine Service.

Demonstrates the complete animation pipeline:
1. Character detection
2. Segmentation and skeleton generation
3. Theme-aware motion selection
4. Animation rendering
5. Export to storage

Usage:
    python services/demo_animation_engine.py <image_path> <theme>

Example:
    python services/demo_animation_engine.py test_images/garlic.png jungle

Requirements:
- TorchServe must be running with the drawn_humanoid_detector and 
  drawn_humanoid_pose_estimator models loaded
- See README for TorchServe setup instructions
"""

import sys
import logging
from pathlib import Path

from services.animation_engine_service import AnimationEngineService
from services.storage_service import LocalStorageService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run animation engine demo."""
    
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python services/demo_animation_engine.py <image_path> <theme>")
        print("\nAvailable themes: jungle, christmas, party, school, ocean, general")
        print("\nExample:")
        print("  python services/demo_animation_engine.py test_images/garlic.png jungle")
        sys.exit(1)
    
    image_path = sys.argv[1]
    theme = sys.argv[2]
    
    # Validate inputs
    if not Path(image_path).exists():
        logger.error(f"Image not found: {image_path}")
        sys.exit(1)
    
    valid_themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
    if theme not in valid_themes:
        logger.warning(f"Invalid theme '{theme}', using 'general' instead")
        theme = 'general'
    
    # Initialize service
    logger.info("Initializing Animation Engine Service...")
    storage_service = LocalStorageService(base_path="uploads")
    animation_service = AnimationEngineService(
        storage_service=storage_service,
        work_dir="uploads/animations"
    )
    
    # Generate a drawing ID
    drawing_id = f"demo-{Path(image_path).stem}"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Starting Animation Pipeline")
    logger.info(f"{'='*60}")
    logger.info(f"Image: {image_path}")
    logger.info(f"Theme: {theme}")
    logger.info(f"Drawing ID: {drawing_id}")
    logger.info(f"{'='*60}\n")
    
    try:
        # Step 1: Detect character
        logger.info("Step 1: Detecting character...")
        detection = animation_service.detect_character(image_path)
        
        if not detection.success:
            logger.error(f"Character detection failed: {detection.error_message}")
            logger.error("\nMake sure TorchServe is running with the required models.")
            logger.error("See README for setup instructions.")
            sys.exit(1)
        
        logger.info(f"✓ Character detected with confidence {detection.confidence:.2f}")
        logger.info(f"  Bounding box: {detection.bbox}")
        
        # Step 2: Generate segmentation
        logger.info("\nStep 2: Generating segmentation and skeleton...")
        work_dir = f"uploads/animations/{drawing_id}"
        segmentation = animation_service.generate_segmentation(
            image_path, detection, work_dir
        )
        
        if not segmentation.success:
            logger.error(f"Segmentation failed: {segmentation.error_message}")
            sys.exit(1)
        
        logger.info(f"✓ Segmentation complete")
        logger.info(f"  Mask: {segmentation.mask_path}")
        logger.info(f"  Skeleton joints: {len(segmentation.skeleton_data['skeleton'])}")
        
        # Step 3: Select motion
        logger.info(f"\nStep 3: Selecting motion for theme '{theme}'...")
        motion = animation_service.select_motion_for_theme(theme)
        logger.info(f"✓ Selected motion: {motion}")
        
        # Step 4: Apply motion and render
        logger.info(f"\nStep 4: Applying motion and rendering animation...")
        animation = animation_service.apply_motion(work_dir, motion)
        
        if not animation.success:
            logger.error(f"Animation failed: {animation.error_message}")
            sys.exit(1)
        
        logger.info(f"✓ Animation rendered")
        logger.info(f"  Output: {animation.animation_path}")
        
        # Step 5: Export to storage
        logger.info(f"\nStep 5: Exporting to storage...")
        animation_url = animation_service.export_animation(
            animation.animation_path, drawing_id
        )
        logger.info(f"✓ Animation exported")
        logger.info(f"  Storage path: {animation_url}")
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Animation Pipeline Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"Animation file: {animation.animation_path}")
        logger.info(f"Storage path: {animation_url}")
        logger.info(f"Working directory: {work_dir}")
        logger.info(f"\nYou can view the animation at:")
        logger.info(f"  {Path(animation.animation_path).absolute()}")
        logger.info(f"\nAdditional files in working directory:")
        logger.info(f"  - texture.png (cropped character)")
        logger.info(f"  - mask.png (segmentation mask)")
        logger.info(f"  - char_cfg.yaml (character configuration)")
        logger.info(f"  - joint_overlay.png (skeleton visualization)")
        logger.info(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        logger.info("\nAnimation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
