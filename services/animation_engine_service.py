"""
Animation Engine Service

Integrates with Facebook Animated Drawings library to animate static drawings.
Handles character detection, segmentation, motion sequence application, and export.

Requirements: 3.1, 3.2, 3.4, 3.5, 11.1, 11.2, 11.3, 11.4
"""

import os
import logging
import random
import shutil
import yaml
import cv2
import json
import requests
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

import animated_drawings.render
from skimage import measure
from scipy import ndimage

from models.animation_data import AnimationData
from services.storage_service import StorageService, LocalStorageService

logger = logging.getLogger(__name__)


@dataclass
class CharacterDetection:
    """Result of character detection."""
    success: bool
    confidence: float = 0.0
    bbox: Optional[Tuple[int, int, int, int]] = None  # (left, top, right, bottom)
    error_message: Optional[str] = None


@dataclass
class SegmentationResult:
    """Result of segmentation mask generation."""
    success: bool
    mask_path: Optional[str] = None
    skeleton_data: Optional[Dict] = None
    cropped_image_path: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class AnimationResult:
    """Result of animation generation."""
    success: bool
    animation_path: Optional[str] = None
    motion_sequence: Optional[str] = None
    error_message: Optional[str] = None


class AnimationEngineService:
    """
    Service for animating drawings using Facebook Animated Drawings library.
    
    Provides:
    - Character detection using pre-trained models
    - Segmentation mask generation
    - Skeleton rigging and joint annotation
    - Motion sequence application
    - Theme-aware motion selection
    - Animation export
    
    Requirements: 3.1, 3.2, 3.4, 3.5, 11.1, 11.2, 11.3, 11.4
    """
    
    # TorchServe endpoints for detection and pose estimation
    DETECTION_URL = "http://localhost:8080/predictions/drawn_humanoid_detector"
    POSE_URL = "http://localhost:8080/predictions/drawn_humanoid_pose_estimator"
    
    # BVH motion files mapping (from theme_manager.py)
    THEME_MOTIONS = {
        'jungle': ['zombie', 'jumping', 'wave_hello'],
        'christmas': ['jesse_dance', 'wave_hello', 'dab'],
        'party': ['jesse_dance', 'jumping', 'dab', 'jumping_jacks'],
        'school': ['wave_hello', 'jumping', 'dab'],
        'ocean': ['wave_hello', 'zombie', 'jesse_dance'],
        'general': ['wave_hello', 'jumping', 'dab']
    }
    
    # Motion file paths
    MOTION_CONFIGS = {
        'dab': 'examples/config/motion/dab.yaml',
        'jumping': 'examples/config/motion/jumping.yaml',
        'wave_hello': 'examples/config/motion/wave_hello.yaml',
        'zombie': 'examples/config/motion/zombie.yaml',
        'jesse_dance': 'examples/config/motion/jesse_dance.yaml',
        'jumping_jacks': 'examples/config/motion/jumping_jacks.yaml'
    }
    
    # Default retarget config
    DEFAULT_RETARGET_CONFIG = 'examples/config/retarget/fair1_ppf.yaml'
    
    def __init__(self, storage_service: Optional[StorageService] = None, 
                 work_dir: str = "uploads/animations"):
        """
        Initialize Animation Engine Service.
        
        Args:
            storage_service: Storage service for saving animation outputs
            work_dir: Working directory for temporary files
        """
        self.storage_service = storage_service or LocalStorageService()
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        logger.info("AnimationEngineService initialized")
    
    def detect_character(self, image_path: str) -> CharacterDetection:
        """
        Detect character in drawing using Facebook Animated Drawings.
        
        Uses TorchServe endpoint to detect drawn humanoids in the image.
        
        Args:
            image_path: Path to the drawing image
            
        Returns:
            CharacterDetection result with bbox and confidence
            
        Requirements: 3.1
        """
        try:
            # Read and preprocess image
            img = cv2.imread(image_path)
            if img is None:
                return CharacterDetection(
                    success=False,
                    error_message=f"Failed to read image: {image_path}"
                )
            
            # Ensure RGB
            if len(img.shape) != 3:
                return CharacterDetection(
                    success=False,
                    error_message=f"Image must have 3 channels (RGB), found {len(img.shape)}"
                )
            
            # Resize if needed
            if np.max(img.shape) > 1000:
                scale = 1000 / np.max(img.shape)
                img = cv2.resize(img, (round(scale * img.shape[1]), round(scale * img.shape[0])))
            
            # Convert to bytes and send to TorchServe
            img_bytes = cv2.imencode('.png', img)[1].tobytes()
            request_data = {'data': img_bytes}
            
            logger.info(f"Sending detection request for {image_path}")
            resp = requests.post(self.DETECTION_URL, files=request_data, verify=False, timeout=30)
            
            if resp is None or resp.status_code >= 300:
                return CharacterDetection(
                    success=False,
                    error_message=f"Detection service error: status {resp.status_code if resp else 'None'}"
                )
            
            detection_results = json.loads(resp.content)
            
            # Check for errors
            if isinstance(detection_results, dict) and 'code' in detection_results:
                return CharacterDetection(
                    success=False,
                    error_message=f"Detection service error: {detection_results}"
                )
            
            # Sort by score
            detection_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Check if any characters detected
            if len(detection_results) == 0:
                return CharacterDetection(
                    success=False,
                    error_message="No drawn humanoids detected in image"
                )
            
            # Use highest scoring detection
            best_detection = detection_results[0]
            bbox = [round(x) for x in best_detection['bbox']]
            
            logger.info(f"Detected {len(detection_results)} humanoids, using best with score {best_detection['score']}")
            
            return CharacterDetection(
                success=True,
                confidence=best_detection['score'],
                bbox=tuple(bbox)
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during character detection: {e}")
            return CharacterDetection(
                success=False,
                error_message=f"Network error: {e}"
            )
        except Exception as e:
            logger.error(f"Error detecting character in {image_path}: {e}")
            return CharacterDetection(
                success=False,
                error_message=f"Detection failed: {e}"
            )
    
    def generate_segmentation(self, image_path: str, detection: CharacterDetection,
                            output_dir: str) -> SegmentationResult:
        """
        Generate segmentation mask and skeleton annotations.
        
        Creates:
        - Segmentation mask
        - Cropped character image
        - Skeleton joint annotations
        - Character configuration file
        
        Args:
            image_path: Path to original image
            detection: CharacterDetection result with bbox
            output_dir: Directory to save outputs
            
        Returns:
            SegmentationResult with paths and skeleton data
            
        Requirements: 3.2
        """
        try:
            outdir = Path(output_dir)
            outdir.mkdir(exist_ok=True, parents=True)
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return SegmentationResult(
                    success=False,
                    error_message=f"Failed to read image: {image_path}"
                )
            
            # Resize if needed
            if np.max(img.shape) > 1000:
                scale = 1000 / np.max(img.shape)
                img = cv2.resize(img, (round(scale * img.shape[1]), round(scale * img.shape[0])))
            
            # Copy original image
            cv2.imwrite(str(outdir / 'image.png'), img)
            
            # Extract bbox and crop
            l, t, r, b = detection.bbox
            cropped = img[t:b, l:r]
            
            # Save bounding box
            with open(str(outdir / 'bounding_box.yaml'), 'w') as f:
                yaml.dump({'left': l, 'top': t, 'right': r, 'bottom': b}, f)
            
            # Generate segmentation mask
            mask = self._segment_character(cropped)
            
            # Get pose estimation
            pose_result = self._estimate_pose(cropped)
            if not pose_result['success']:
                return SegmentationResult(
                    success=False,
                    error_message=pose_result['error']
                )
            
            kpts = pose_result['keypoints']
            
            # Build skeleton
            skeleton = self._build_skeleton(kpts)
            
            # Create character config
            char_cfg = {
                'skeleton': skeleton,
                'height': cropped.shape[0],
                'width': cropped.shape[1]
            }
            
            # Save outputs
            cropped_rgba = cv2.cvtColor(cropped, cv2.COLOR_BGR2BGRA)
            texture_path = str(outdir / 'texture.png')
            mask_path = str(outdir / 'mask.png')
            char_cfg_path = str(outdir / 'char_cfg.yaml')
            
            cv2.imwrite(texture_path, cropped_rgba)
            cv2.imwrite(mask_path, mask)
            
            with open(char_cfg_path, 'w') as f:
                yaml.dump(char_cfg, f)
            
            # Create joint overlay for visualization
            joint_overlay = cropped_rgba.copy()
            for joint in skeleton:
                x, y = joint['loc']
                name = joint['name']
                cv2.circle(joint_overlay, (int(x), int(y)), 5, (0, 0, 0), 5)
                cv2.putText(joint_overlay, name, (int(x), int(y+15)), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, 2)
            cv2.imwrite(str(outdir / 'joint_overlay.png'), joint_overlay)
            
            logger.info(f"Generated segmentation and skeleton for {image_path}")
            
            return SegmentationResult(
                success=True,
                mask_path=mask_path,
                skeleton_data=char_cfg,
                cropped_image_path=texture_path
            )
            
        except Exception as e:
            logger.error(f"Error generating segmentation: {e}")
            return SegmentationResult(
                success=False,
                error_message=f"Segmentation failed: {e}"
            )
    
    def _segment_character(self, img: np.ndarray) -> np.ndarray:
        """
        Segment character from background using adaptive thresholding.
        
        Args:
            img: Cropped character image
            
        Returns:
            Binary mask (255 = character, 0 = background)
        """
        # Threshold
        img_gray = np.min(img, axis=2)
        img_thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 115, 8)
        img_thresh = cv2.bitwise_not(img_thresh)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img_morph = cv2.morphologyEx(img_thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        img_morph = cv2.morphologyEx(img_morph, cv2.MORPH_DILATE, kernel, iterations=2)
        
        # Floodfill from edges
        mask = np.zeros([img_morph.shape[0]+2, img_morph.shape[1]+2], np.uint8)
        mask[1:-1, 1:-1] = img_morph.copy()
        
        im_floodfill = np.full(img_morph.shape, 255, np.uint8)
        
        h, w = img_morph.shape[:2]
        for x in range(0, w-1, 10):
            cv2.floodFill(im_floodfill, mask, (x, 0), 0)
            cv2.floodFill(im_floodfill, mask, (x, h-1), 0)
        for y in range(0, h-1, 10):
            cv2.floodFill(im_floodfill, mask, (0, y), 0)
            cv2.floodFill(im_floodfill, mask, (w-1, y), 0)
        
        # Clear edges
        im_floodfill[0, :] = 0
        im_floodfill[-1, :] = 0
        im_floodfill[:, 0] = 0
        im_floodfill[:, -1] = 0
        
        # Retain largest contour
        mask2 = cv2.bitwise_not(im_floodfill)
        final_mask = None
        biggest = 0
        
        contours = measure.find_contours(mask2, 0.0)
        for c in contours:
            x = np.zeros(mask2.T.shape, np.uint8)
            cv2.fillPoly(x, [np.int32(c)], 1)
            size = len(np.where(x == 1)[0])
            if size > biggest:
                final_mask = x
                biggest = size
        
        if final_mask is None:
            raise ValueError("No contours found in image")
        
        final_mask = ndimage.binary_fill_holes(final_mask).astype(int)
        final_mask = 255 * final_mask.astype(np.uint8)
        
        return final_mask.T
    
    def _estimate_pose(self, cropped_img: np.ndarray) -> Dict:
        """
        Estimate pose/skeleton keypoints using TorchServe.
        
        Args:
            cropped_img: Cropped character image
            
        Returns:
            Dict with 'success', 'keypoints', and 'error' keys
        """
        try:
            img_bytes = cv2.imencode('.png', cropped_img)[1].tobytes()
            data_file = {'data': img_bytes}
            
            resp = requests.post(self.POSE_URL, files=data_file, verify=False, timeout=30)
            
            if resp is None or resp.status_code >= 300:
                return {
                    'success': False,
                    'error': f"Pose estimation service error: status {resp.status_code if resp else 'None'}"
                }
            
            pose_results = json.loads(resp.content)
            
            # Check for errors
            if isinstance(pose_results, dict) and 'code' in pose_results:
                return {
                    'success': False,
                    'error': f"Pose estimation error: {pose_results}"
                }
            
            # Validate skeleton count
            if len(pose_results) == 0:
                return {
                    'success': False,
                    'error': "No skeleton detected in character bounding box"
                }
            
            if len(pose_results) > 1:
                logger.warning(f"Detected {len(pose_results)} skeletons, expected 1. Using first.")
            
            # Extract keypoints
            kpts = np.array(pose_results[0]['keypoints'])[:, :2]
            
            return {
                'success': True,
                'keypoints': kpts
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Pose estimation failed: {e}"
            }
    
    def _build_skeleton(self, kpts: np.ndarray) -> List[Dict]:
        """
        Build skeleton rig from keypoints.
        
        Args:
            kpts: Keypoint coordinates array
            
        Returns:
            List of skeleton joint dictionaries
        """
        skeleton = []
        skeleton.append({'loc': [round(x) for x in (kpts[11]+kpts[12])/2], 'name': 'root', 'parent': None})
        skeleton.append({'loc': [round(x) for x in (kpts[11]+kpts[12])/2], 'name': 'hip', 'parent': 'root'})
        skeleton.append({'loc': [round(x) for x in (kpts[5]+kpts[6])/2], 'name': 'torso', 'parent': 'hip'})
        skeleton.append({'loc': [round(x) for x in kpts[0]], 'name': 'neck', 'parent': 'torso'})
        skeleton.append({'loc': [round(x) for x in kpts[6]], 'name': 'right_shoulder', 'parent': 'torso'})
        skeleton.append({'loc': [round(x) for x in kpts[8]], 'name': 'right_elbow', 'parent': 'right_shoulder'})
        skeleton.append({'loc': [round(x) for x in kpts[10]], 'name': 'right_hand', 'parent': 'right_elbow'})
        skeleton.append({'loc': [round(x) for x in kpts[5]], 'name': 'left_shoulder', 'parent': 'torso'})
        skeleton.append({'loc': [round(x) for x in kpts[7]], 'name': 'left_elbow', 'parent': 'left_shoulder'})
        skeleton.append({'loc': [round(x) for x in kpts[9]], 'name': 'left_hand', 'parent': 'left_elbow'})
        skeleton.append({'loc': [round(x) for x in kpts[12]], 'name': 'right_hip', 'parent': 'root'})
        skeleton.append({'loc': [round(x) for x in kpts[14]], 'name': 'right_knee', 'parent': 'right_hip'})
        skeleton.append({'loc': [round(x) for x in kpts[16]], 'name': 'right_foot', 'parent': 'right_knee'})
        skeleton.append({'loc': [round(x) for x in kpts[11]], 'name': 'left_hip', 'parent': 'root'})
        skeleton.append({'loc': [round(x) for x in kpts[13]], 'name': 'left_knee', 'parent': 'left_hip'})
        skeleton.append({'loc': [round(x) for x in kpts[15]], 'name': 'left_foot', 'parent': 'left_knee'})
        
        return skeleton
    
    def select_motion_for_theme(self, theme: str) -> str:
        """
        Select appropriate motion sequence based on theme.
        
        Args:
            theme: Theme name (jungle, christmas, party, school, ocean, general)
            
        Returns:
            Motion sequence name
            
        Requirements: 11.1, 11.2, 11.3, 11.4
        """
        motions = self.THEME_MOTIONS.get(theme, self.THEME_MOTIONS['general'])
        selected = random.choice(motions)
        logger.info(f"Selected motion '{selected}' for theme '{theme}'")
        return selected
    
    def apply_motion(self, char_anno_dir: str, motion_sequence: str,
                    retarget_cfg: Optional[str] = None) -> AnimationResult:
        """
        Apply motion sequence to character and generate animation.
        
        Args:
            char_anno_dir: Directory with character annotations
            motion_sequence: Name of motion sequence to apply
            retarget_cfg: Optional retarget config path
            
        Returns:
            AnimationResult with animation file path
            
        Requirements: 3.4, 3.5
        """
        try:
            # Get motion config path
            motion_cfg = self.MOTION_CONFIGS.get(motion_sequence)
            if motion_cfg is None:
                return AnimationResult(
                    success=False,
                    error_message=f"Unknown motion sequence: {motion_sequence}"
                )
            
            # Use default retarget config if not provided
            if retarget_cfg is None:
                retarget_cfg = self.DEFAULT_RETARGET_CONFIG
            
            # Verify files exist
            char_cfg_path = Path(char_anno_dir) / 'char_cfg.yaml'
            if not char_cfg_path.exists():
                return AnimationResult(
                    success=False,
                    error_message=f"Character config not found: {char_cfg_path}"
                )
            
            # Create animated drawing config
            animated_drawing_dict = {
                'character_cfg': str(char_cfg_path.resolve()),
                'motion_cfg': str(Path(motion_cfg).resolve()),
                'retarget_cfg': str(Path(retarget_cfg).resolve())
            }
            
            # Create MVC config
            output_video_path = str(Path(char_anno_dir) / 'video.gif')
            mvc_cfg = {
                'scene': {'ANIMATED_CHARACTERS': [animated_drawing_dict]},
                'controller': {
                    'MODE': 'video_render',
                    'OUTPUT_VIDEO_PATH': output_video_path
                }
            }
            
            # Write MVC config
            mvc_cfg_path = str(Path(char_anno_dir) / 'mvc_cfg.yaml')
            with open(mvc_cfg_path, 'w') as f:
                yaml.dump(dict(mvc_cfg), f)
            
            # Render animation
            logger.info(f"Rendering animation with motion '{motion_sequence}'")
            animated_drawings.render.start(mvc_cfg_path)
            
            # Verify output was created
            if not Path(output_video_path).exists():
                return AnimationResult(
                    success=False,
                    error_message="Animation rendering completed but output file not found"
                )
            
            logger.info(f"Animation created successfully: {output_video_path}")
            
            return AnimationResult(
                success=True,
                animation_path=output_video_path,
                motion_sequence=motion_sequence
            )
            
        except Exception as e:
            logger.error(f"Error applying motion: {e}")
            return AnimationResult(
                success=False,
                error_message=f"Motion application failed: {e}"
            )
    
    def export_animation(self, animation_path: str, drawing_id: str) -> str:
        """
        Export animation to storage.
        
        Args:
            animation_path: Path to animation file
            drawing_id: Drawing ID for organizing storage
            
        Returns:
            Storage path/URL for animation
        """
        try:
            # Store animation using storage service
            storage_path = f"animations/{drawing_id}/video.gif"
            stored_path = self.storage_service.store(animation_path, storage_path)
            logger.info(f"Exported animation to storage: {stored_path}")
            return stored_path
        except Exception as e:
            logger.error(f"Failed to export animation: {e}")
            raise
    
    def animate_drawing(self, image_path: str, drawing_id: str, theme: str) -> AnimationData:
        """
        Complete animation pipeline for a drawing.
        
        Steps:
        1. Detect character
        2. Generate segmentation and skeleton
        3. Select motion based on theme
        4. Apply motion and render animation
        5. Export to storage
        
        Args:
            image_path: Path to drawing image
            drawing_id: Drawing ID
            theme: Theme name for motion selection
            
        Returns:
            AnimationData with all results
            
        Raises:
            ValueError: If animation fails
            
        Requirements: 3.1, 3.2, 3.4, 3.5, 11.1, 11.2, 11.3, 11.4
        """
        # Create working directory for this drawing
        work_dir = self.work_dir / drawing_id
        work_dir.mkdir(exist_ok=True, parents=True)
        
        try:
            # Step 1: Detect character
            logger.info(f"Starting animation pipeline for drawing {drawing_id}")
            detection = self.detect_character(image_path)
            
            if not detection.success:
                logger.warning(f"Character detection failed: {detection.error_message}")
                return AnimationData(
                    id=drawing_id,
                    drawing_id=drawing_id,
                    character_detected=False,
                    segmentation_mask_url=None,
                    skeleton_data=None,
                    motion_sequence=None,
                    animation_file_url=None,
                    sprite_sheet_url=None
                )
            
            # Step 2: Generate segmentation
            segmentation = self.generate_segmentation(image_path, detection, str(work_dir))
            
            if not segmentation.success:
                logger.error(f"Segmentation failed: {segmentation.error_message}")
                raise ValueError(f"Segmentation failed: {segmentation.error_message}")
            
            # Step 3: Select motion
            motion_sequence = self.select_motion_for_theme(theme)
            
            # Step 4: Apply motion
            animation = self.apply_motion(str(work_dir), motion_sequence)
            
            if not animation.success:
                logger.error(f"Animation failed: {animation.error_message}")
                raise ValueError(f"Animation failed: {animation.error_message}")
            
            # Step 5: Export to storage
            animation_url = self.export_animation(animation.animation_path, drawing_id)
            
            # Store mask
            mask_storage_path = f"masks/{drawing_id}/mask.png"
            mask_url = self.storage_service.store(segmentation.mask_path, mask_storage_path)
            
            logger.info(f"Animation pipeline completed successfully for drawing {drawing_id}")
            
            return AnimationData(
                id=drawing_id,
                drawing_id=drawing_id,
                character_detected=True,
                segmentation_mask_url=mask_url,
                skeleton_data=segmentation.skeleton_data,
                motion_sequence=motion_sequence,
                animation_file_url=animation_url,
                sprite_sheet_url=None  # Not generating sprite sheets in this implementation
            )
            
        except Exception as e:
            logger.error(f"Animation pipeline failed for drawing {drawing_id}: {e}")
            raise
        finally:
            # Clean up working directory
            try:
                shutil.rmtree(work_dir)
                logger.debug(f"Cleaned up working directory: {work_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up working directory {work_dir}: {e}")
