#!/usr/bin/env python3
"""
Integration test for motion configuration.

Tests the complete motion selection and configuration flow.
"""

import unittest
import os
from pathlib import Path

from services.animation_engine_service import AnimationEngineService
from services.theme_manager import ThemeManagerService


class TestMotionIntegration(unittest.TestCase):
    """Integration tests for motion configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.anim_service = AnimationEngineService()
        self.theme_service = ThemeManagerService()
    
    def test_all_motion_files_exist(self):
        """Test that all referenced BVH files exist."""
        for motion_name, config_path in self.anim_service.MOTION_CONFIGS.items():
            # Check config file exists
            self.assertTrue(
                Path(config_path).exists(),
                f"Motion config file not found: {config_path}"
            )
            
            # Read config and check BVH file exists
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            bvh_path = config['filepath']
            self.assertTrue(
                Path(bvh_path).exists(),
                f"BVH file not found: {bvh_path} (referenced by {motion_name})"
            )
    
    def test_theme_motion_selection_produces_valid_motions(self):
        """Test that motion selection always returns valid motion names."""
        themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
        
        for theme in themes:
            for _ in range(10):  # Test multiple selections
                motion = self.anim_service.select_motion_for_theme(theme)
                
                # Motion should be in the theme's motion list
                self.assertIn(
                    motion,
                    self.anim_service.THEME_MOTIONS[theme],
                    f"Selected motion '{motion}' not in theme '{theme}' motion list"
                )
                
                # Motion should have a config file
                self.assertIn(
                    motion,
                    self.anim_service.MOTION_CONFIGS,
                    f"Selected motion '{motion}' has no config file"
                )
    
    def test_invalid_theme_fallback_produces_valid_motions(self):
        """Test that invalid themes fall back to general theme motions."""
        invalid_themes = ['invalid', 'nonexistent', 'test', 'unknown', '']
        general_motions = set(self.anim_service.THEME_MOTIONS['general'])
        
        for invalid_theme in invalid_themes:
            motion = self.anim_service.select_motion_for_theme(invalid_theme)
            
            # Should be a general theme motion
            self.assertIn(
                motion,
                general_motions,
                f"Invalid theme '{invalid_theme}' did not fall back to general motions"
            )
    
    def test_motion_config_paths_are_valid(self):
        """Test that all motion config paths are valid and accessible."""
        for motion_name, config_path in self.anim_service.MOTION_CONFIGS.items():
            path = Path(config_path)
            
            # Path should exist
            self.assertTrue(
                path.exists(),
                f"Config path does not exist: {config_path}"
            )
            
            # Path should be a file
            self.assertTrue(
                path.is_file(),
                f"Config path is not a file: {config_path}"
            )
            
            # File should be readable
            self.assertTrue(
                os.access(path, os.R_OK),
                f"Config file is not readable: {config_path}"
            )
    
    def test_service_consistency(self):
        """Test that AnimationEngineService and ThemeManagerService are consistent."""
        # Both should define the same themes
        anim_themes = set(self.anim_service.THEME_MOTIONS.keys())
        theme_themes = set(self.theme_service.THEME_MOTIONS.keys())
        
        self.assertEqual(
            anim_themes,
            theme_themes,
            "AnimationEngineService and ThemeManagerService define different themes"
        )
        
        # Motion mappings should be identical
        for theme in anim_themes:
            anim_motions = set(self.anim_service.THEME_MOTIONS[theme])
            theme_motions = set(self.theme_service.THEME_MOTIONS[theme])
            
            self.assertEqual(
                anim_motions,
                theme_motions,
                f"Motion mappings differ for theme '{theme}'"
            )
    
    def test_all_themes_have_at_least_one_motion(self):
        """Test that every theme has at least one motion configured."""
        for theme, motions in self.anim_service.THEME_MOTIONS.items():
            self.assertGreater(
                len(motions),
                0,
                f"Theme '{theme}' has no motions configured"
            )
    
    def test_all_referenced_motions_have_configs(self):
        """Test that all motions referenced in themes have config files."""
        all_referenced_motions = set()
        for motions in self.anim_service.THEME_MOTIONS.values():
            all_referenced_motions.update(motions)
        
        for motion in all_referenced_motions:
            self.assertIn(
                motion,
                self.anim_service.MOTION_CONFIGS,
                f"Motion '{motion}' is referenced but has no config file"
            )
    
    def test_motion_selection_distribution(self):
        """Test that motion selection has reasonable distribution."""
        theme = 'party'  # Has 4 motions
        selections = {}
        num_samples = 100
        
        for _ in range(num_samples):
            motion = self.anim_service.select_motion_for_theme(theme)
            selections[motion] = selections.get(motion, 0) + 1
        
        # All motions should be selected at least once in 100 samples
        expected_motions = set(self.anim_service.THEME_MOTIONS[theme])
        selected_motions = set(selections.keys())
        
        self.assertEqual(
            expected_motions,
            selected_motions,
            f"Not all motions were selected in {num_samples} samples"
        )
        
        # Each motion should be selected at least 10% of the time
        # (with 4 motions, expected is 25%, so 10% is reasonable lower bound)
        for motion, count in selections.items():
            percentage = (count / num_samples) * 100
            self.assertGreater(
                percentage,
                10.0,
                f"Motion '{motion}' only selected {percentage:.1f}% of the time"
            )


if __name__ == '__main__':
    unittest.main()
