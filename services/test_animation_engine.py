"""
Unit tests for Animation Engine Service.

Tests character detection, segmentation, motion selection, and animation pipeline.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import cv2

from services.animation_engine_service import (
    AnimationEngineService,
    CharacterDetection,
    SegmentationResult,
    AnimationResult
)
from models.animation_data import AnimationData


@pytest.fixture
def animation_service():
    """Create animation service with temporary work directory."""
    temp_dir = tempfile.mkdtemp()
    service = AnimationEngineService(work_dir=temp_dir)
    yield service
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def test_image():
    """Create a simple test image."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    # Create a simple RGB image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.imwrite(temp_file.name, img)
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


class TestMotionSelection:
    """Test theme-aware motion selection."""
    
    def test_select_motion_for_jungle_theme(self, animation_service):
        """Test motion selection for jungle theme."""
        motion = animation_service.select_motion_for_theme('jungle')
        assert motion in ['zombie', 'jumping', 'wave_hello']
    
    def test_select_motion_for_christmas_theme(self, animation_service):
        """Test motion selection for christmas theme."""
        motion = animation_service.select_motion_for_theme('christmas')
        assert motion in ['jesse_dance', 'wave_hello', 'dab']
    
    def test_select_motion_for_party_theme(self, animation_service):
        """Test motion selection for party theme."""
        motion = animation_service.select_motion_for_theme('party')
        assert motion in ['jesse_dance', 'jumping', 'dab', 'jumping_jacks']
    
    def test_select_motion_for_school_theme(self, animation_service):
        """Test motion selection for school theme."""
        motion = animation_service.select_motion_for_theme('school')
        assert motion in ['wave_hello', 'jumping', 'dab']
    
    def test_select_motion_for_ocean_theme(self, animation_service):
        """Test motion selection for ocean theme."""
        motion = animation_service.select_motion_for_theme('ocean')
        assert motion in ['wave_hello', 'zombie', 'jesse_dance']
    
    def test_select_motion_for_general_theme(self, animation_service):
        """Test motion selection for general/default theme."""
        motion = animation_service.select_motion_for_theme('general')
        assert motion in ['wave_hello', 'jumping', 'dab']
    
    def test_select_motion_for_invalid_theme_uses_default(self, animation_service):
        """Test that invalid theme falls back to general theme motions."""
        motion = animation_service.select_motion_for_theme('invalid_theme')
        assert motion in ['wave_hello', 'jumping', 'dab']


class TestCharacterDetection:
    """Test character detection functionality."""
    
    def test_detect_character_with_invalid_image_path(self, animation_service):
        """Test detection with non-existent image."""
        result = animation_service.detect_character('/nonexistent/image.png')
        assert not result.success
        assert 'Failed to read image' in result.error_message
    
    @patch('services.animation_engine_service.requests.post')
    def test_detect_character_with_network_error(self, mock_post, animation_service, test_image):
        """Test detection handles network errors gracefully."""
        mock_post.side_effect = Exception("Network error")
        
        result = animation_service.detect_character(test_image)
        assert not result.success
        assert 'Detection failed' in result.error_message
    
    @patch('services.animation_engine_service.requests.post')
    def test_detect_character_with_no_detections(self, mock_post, animation_service, test_image):
        """Test detection when no characters found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'[]'
        mock_post.return_value = mock_response
        
        result = animation_service.detect_character(test_image)
        assert not result.success
        assert 'No drawn humanoids detected' in result.error_message
    
    @patch('services.animation_engine_service.requests.post')
    def test_detect_character_success(self, mock_post, animation_service, test_image):
        """Test successful character detection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'[{"bbox": [10, 20, 100, 200], "score": 0.95}]'
        mock_post.return_value = mock_response
        
        result = animation_service.detect_character(test_image)
        assert result.success
        assert result.confidence == 0.95
        assert result.bbox == (10, 20, 100, 200)


class TestSkeletonBuilding:
    """Test skeleton building from keypoints."""
    
    def test_build_skeleton_structure(self, animation_service):
        """Test skeleton has correct structure."""
        # Create mock keypoints (17 keypoints with x,y coordinates)
        kpts = np.array([[50, 50]] * 17)  # Simplified keypoints
        
        skeleton = animation_service._build_skeleton(kpts)
        
        # Verify skeleton structure
        assert len(skeleton) == 16  # Should have 16 joints
        
        # Check root joint
        assert skeleton[0]['name'] == 'root'
        assert skeleton[0]['parent'] is None
        
        # Check all joints have required fields
        for joint in skeleton:
            assert 'name' in joint
            assert 'loc' in joint
            assert 'parent' in joint
            assert len(joint['loc']) == 2  # x, y coordinates


class TestSegmentation:
    """Test segmentation functionality."""
    
    def test_segment_character_with_simple_image(self, animation_service):
        """Test segmentation produces binary mask."""
        # Create a simple test image with a dark shape on white background
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        # Draw a dark rectangle in the center
        img[30:70, 30:70] = [50, 50, 50]
        
        mask = animation_service._segment_character(img)
        
        # Verify mask properties
        assert mask.shape == (100, 100)
        assert mask.dtype == np.uint8
        assert np.all((mask == 0) | (mask == 255))  # Binary mask
        assert np.sum(mask == 255) > 0  # Has some foreground pixels


class TestAnimationExport:
    """Test animation export functionality."""
    
    def test_export_animation_creates_storage_path(self, animation_service):
        """Test animation export stores file correctly."""
        # Create a temporary animation file
        temp_file = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
        temp_file.write(b'fake gif data')
        temp_file.close()
        
        try:
            drawing_id = 'test-drawing-123'
            result = animation_service.export_animation(temp_file.name, drawing_id)
            
            # Verify storage path format
            assert drawing_id in result
            assert 'animations' in result
            
        finally:
            os.unlink(temp_file.name)


class TestThemeMotionMapping:
    """Test theme to motion sequence mapping."""
    
    def test_all_themes_have_motion_mappings(self, animation_service):
        """Test all defined themes have motion sequences."""
        themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
        
        for theme in themes:
            motions = animation_service.THEME_MOTIONS.get(theme)
            assert motions is not None
            assert len(motions) > 0
            assert all(isinstance(m, str) for m in motions)
    
    def test_all_motions_have_config_files(self, animation_service):
        """Test all motion sequences have corresponding config files."""
        all_motions = set()
        for motions in animation_service.THEME_MOTIONS.values():
            all_motions.update(motions)
        
        for motion in all_motions:
            assert motion in animation_service.MOTION_CONFIGS
            # Note: We don't check file existence here as it depends on the environment


class TestAnimationResult:
    """Test AnimationResult dataclass."""
    
    def test_animation_result_success(self):
        """Test successful animation result."""
        result = AnimationResult(
            success=True,
            animation_path='/path/to/video.gif',
            motion_sequence='dab'
        )
        assert result.success
        assert result.animation_path == '/path/to/video.gif'
        assert result.motion_sequence == 'dab'
        assert result.error_message is None
    
    def test_animation_result_failure(self):
        """Test failed animation result."""
        result = AnimationResult(
            success=False,
            error_message='Animation failed'
        )
        assert not result.success
        assert result.error_message == 'Animation failed'
        assert result.animation_path is None


class TestCharacterDetectionResult:
    """Test CharacterDetection dataclass."""
    
    def test_character_detection_success(self):
        """Test successful detection result."""
        result = CharacterDetection(
            success=True,
            confidence=0.95,
            bbox=(10, 20, 100, 200)
        )
        assert result.success
        assert result.confidence == 0.95
        assert result.bbox == (10, 20, 100, 200)
    
    def test_character_detection_failure(self):
        """Test failed detection result."""
        result = CharacterDetection(
            success=False,
            error_message='No character detected'
        )
        assert not result.success
        assert result.error_message == 'No character detected'
        assert result.bbox is None


class TestSegmentationResult:
    """Test SegmentationResult dataclass."""
    
    def test_segmentation_result_success(self):
        """Test successful segmentation result."""
        result = SegmentationResult(
            success=True,
            mask_path='/path/to/mask.png',
            skeleton_data={'skeleton': []},
            cropped_image_path='/path/to/texture.png'
        )
        assert result.success
        assert result.mask_path == '/path/to/mask.png'
        assert result.skeleton_data is not None
    
    def test_segmentation_result_failure(self):
        """Test failed segmentation result."""
        result = SegmentationResult(
            success=False,
            error_message='Segmentation failed'
        )
        assert not result.success
        assert result.error_message == 'Segmentation failed'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
