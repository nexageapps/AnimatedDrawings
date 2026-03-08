"""
Test Motion Configuration

Tests for verifying motion sequence configuration and theme-motion mapping.

Requirements: 11.5
"""

import unittest
from services.animation_engine_service import AnimationEngineService
from services.theme_manager import ThemeManagerService


class TestMotionConfiguration(unittest.TestCase):
    """Test motion configuration and theme-motion mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.animation_service = AnimationEngineService()
        self.theme_service = ThemeManagerService()
    
    def test_all_themes_have_motions(self):
        """Test that all themes have at least one motion defined."""
        expected_themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
        
        for theme in expected_themes:
            motions = self.animation_service.THEME_MOTIONS.get(theme)
            self.assertIsNotNone(motions, f"Theme '{theme}' has no motions defined")
            self.assertGreater(len(motions), 0, f"Theme '{theme}' has empty motion list")
    
    def test_theme_motion_consistency(self):
        """Test that theme-motion mappings are consistent between services."""
        anim_themes = set(self.animation_service.THEME_MOTIONS.keys())
        theme_themes = set(self.theme_service.THEME_MOTIONS.keys())
        
        # Both services should have the same themes
        self.assertEqual(anim_themes, theme_themes,
                        "Theme sets differ between AnimationEngine and ThemeManager")
        
        # Motion lists should be identical for each theme
        for theme in anim_themes:
            anim_motions = set(self.animation_service.THEME_MOTIONS[theme])
            theme_motions = set(self.theme_service.THEME_MOTIONS[theme])
            self.assertEqual(anim_motions, theme_motions,
                           f"Motion lists differ for theme '{theme}'")
    
    def test_all_motions_have_configs(self):
        """Test that all referenced motions have configuration files."""
        # Collect all referenced motions
        all_motions = set()
        for motions in self.animation_service.THEME_MOTIONS.values():
            all_motions.update(motions)
        
        # Check each motion has a config
        for motion in all_motions:
            self.assertIn(motion, self.animation_service.MOTION_CONFIGS,
                         f"Motion '{motion}' has no config file defined")
    
    def test_motion_selection_for_all_themes(self):
        """Test that motion selection works for all themes."""
        themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
        
        for theme in themes:
            motion = self.animation_service.select_motion_for_theme(theme)
            
            # Motion should be in the theme's motion list
            expected_motions = self.animation_service.THEME_MOTIONS[theme]
            self.assertIn(motion, expected_motions,
                         f"Selected motion '{motion}' not in theme '{theme}' motion list")
    
    def test_invalid_theme_fallback(self):
        """Test that invalid themes fall back to general theme."""
        invalid_themes = ['invalid', 'nonexistent', '', None]
        general_motions = set(self.animation_service.THEME_MOTIONS['general'])
        
        for invalid_theme in invalid_themes:
            motion = self.animation_service.select_motion_for_theme(invalid_theme)
            self.assertIn(motion, general_motions,
                         f"Invalid theme '{invalid_theme}' did not fall back to general motions")
    
    def test_jungle_theme_motions(self):
        """Test jungle theme has appropriate motions."""
        expected_motions = {'zombie', 'jumping', 'wave_hello'}
        actual_motions = set(self.animation_service.THEME_MOTIONS['jungle'])
        self.assertEqual(actual_motions, expected_motions,
                        "Jungle theme motions do not match expected")
    
    def test_christmas_theme_motions(self):
        """Test christmas theme has festive motions."""
        expected_motions = {'jesse_dance', 'wave_hello', 'dab'}
        actual_motions = set(self.animation_service.THEME_MOTIONS['christmas'])
        self.assertEqual(actual_motions, expected_motions,
                        "Christmas theme motions do not match expected")
    
    def test_party_theme_motions(self):
        """Test party theme has celebratory motions."""
        expected_motions = {'jesse_dance', 'jumping', 'dab', 'jumping_jacks'}
        actual_motions = set(self.animation_service.THEME_MOTIONS['party'])
        self.assertEqual(actual_motions, expected_motions,
                        "Party theme motions do not match expected")
    
    def test_school_theme_motions(self):
        """Test school theme has educational/playful motions."""
        expected_motions = {'wave_hello', 'jumping', 'dab'}
        actual_motions = set(self.animation_service.THEME_MOTIONS['school'])
        self.assertEqual(actual_motions, expected_motions,
                        "School theme motions do not match expected")
    
    def test_ocean_theme_motions(self):
        """Test ocean theme has swimming/floating motions."""
        expected_motions = {'wave_hello', 'zombie', 'jesse_dance'}
        actual_motions = set(self.animation_service.THEME_MOTIONS['ocean'])
        self.assertEqual(actual_motions, expected_motions,
                        "Ocean theme motions do not match expected")
    
    def test_general_theme_motions(self):
        """Test general theme has default motions."""
        expected_motions = {'wave_hello', 'jumping', 'dab'}
        actual_motions = set(self.animation_service.THEME_MOTIONS['general'])
        self.assertEqual(actual_motions, expected_motions,
                        "General theme motions do not match expected")
    
    def test_motion_selection_variety(self):
        """Test that motion selection provides variety (not always the same)."""
        theme = 'party'  # Has 4 motions
        selected_motions = set()
        
        # Select motion 20 times
        for _ in range(20):
            motion = self.animation_service.select_motion_for_theme(theme)
            selected_motions.add(motion)
        
        # Should have selected at least 2 different motions (statistically very likely)
        self.assertGreaterEqual(len(selected_motions), 2,
                               "Motion selection does not provide variety")
    
    def test_all_motion_configs_defined(self):
        """Test that all expected motion configs are defined."""
        expected_configs = {
            'dab', 'jumping', 'wave_hello', 'zombie', 
            'jesse_dance', 'jumping_jacks'
        }
        actual_configs = set(self.animation_service.MOTION_CONFIGS.keys())
        self.assertEqual(actual_configs, expected_configs,
                        "Motion configs do not match expected set")
    
    def test_motion_config_paths(self):
        """Test that motion config paths follow expected pattern."""
        for motion_name, config_path in self.animation_service.MOTION_CONFIGS.items():
            # Should be in examples/config/motion/ directory
            self.assertTrue(config_path.startswith('examples/config/motion/'),
                          f"Motion config path '{config_path}' not in expected directory")
            
            # Should end with .yaml
            self.assertTrue(config_path.endswith('.yaml'),
                          f"Motion config path '{config_path}' does not end with .yaml")
            
            # Should contain the motion name
            self.assertIn(motion_name, config_path,
                         f"Motion config path '{config_path}' does not contain motion name '{motion_name}'")


class TestMotionUsageStatistics(unittest.TestCase):
    """Test motion usage statistics across themes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.animation_service = AnimationEngineService()
    
    def test_wave_hello_most_used(self):
        """Test that wave_hello is used by most themes."""
        motion_usage = self._count_motion_usage()
        
        # wave_hello should be used by at least 4 themes
        self.assertGreaterEqual(motion_usage.get('wave_hello', 0), 4,
                               "wave_hello should be used by at least 4 themes")
    
    def test_all_motions_used(self):
        """Test that all defined motions are used by at least one theme."""
        motion_usage = self._count_motion_usage()
        
        for motion in self.animation_service.MOTION_CONFIGS.keys():
            self.assertGreater(motion_usage.get(motion, 0), 0,
                             f"Motion '{motion}' is not used by any theme")
    
    def test_party_has_most_motions(self):
        """Test that party theme has the most motion options."""
        theme_motion_counts = {
            theme: len(motions)
            for theme, motions in self.animation_service.THEME_MOTIONS.items()
        }
        
        # Party should have 4 motions (the most)
        self.assertEqual(theme_motion_counts['party'], 4,
                        "Party theme should have 4 motions")
        
        # Party should have at least as many as any other theme
        max_count = max(theme_motion_counts.values())
        self.assertEqual(theme_motion_counts['party'], max_count,
                        "Party theme should have the most motion options")
    
    def _count_motion_usage(self):
        """Count how many themes use each motion."""
        motion_usage = {}
        for theme, motions in self.animation_service.THEME_MOTIONS.items():
            for motion in motions:
                motion_usage[motion] = motion_usage.get(motion, 0) + 1
        return motion_usage


if __name__ == '__main__':
    unittest.main()
