#!/usr/bin/env python3
"""
Motion Configuration Verification Script

Verifies that all motion files, configuration files, and theme mappings
are correctly configured for the Themed Animation Platform.

Requirements: 11.5
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.animation_engine_service import AnimationEngineService
from services.theme_manager import ThemeManagerService


class MotionConfigVerifier:
    """Verifies motion configuration completeness and correctness."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        
        # Get mappings from services
        self.animation_service = AnimationEngineService()
        self.theme_service = ThemeManagerService()
        
        self.motion_configs = self.animation_service.MOTION_CONFIGS
        self.theme_motions_anim = self.animation_service.THEME_MOTIONS
        self.theme_motions_theme = self.theme_service.THEME_MOTIONS
    
    def verify_all(self) -> bool:
        """
        Run all verification checks.
        
        Returns:
            True if all checks pass, False otherwise
        """
        print("=" * 70)
        print("Motion Configuration Verification")
        print("=" * 70)
        print()
        
        # Run all checks
        self.verify_motion_config_files()
        self.verify_bvh_files()
        self.verify_theme_motion_consistency()
        self.verify_motion_references()
        self.verify_theme_coverage()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0
    
    def verify_motion_config_files(self):
        """Verify all motion configuration YAML files exist."""
        print("Checking motion configuration files...")
        
        for motion_name, config_path in self.motion_configs.items():
            if not os.path.exists(config_path):
                self.errors.append(
                    f"Motion config file not found: {config_path} (for motion '{motion_name}')"
                )
            else:
                # Try to load and validate YAML
                try:
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    # Check required fields
                    required_fields = ['filepath', 'groundplane_joint', 
                                     'forward_perp_joint_vectors', 'scale', 'up']
                    missing_fields = [f for f in required_fields if f not in config]
                    
                    if missing_fields:
                        self.errors.append(
                            f"Motion config {config_path} missing fields: {missing_fields}"
                        )
                    else:
                        self.successes.append(
                            f"✓ Motion config '{motion_name}': {config_path}"
                        )
                except Exception as e:
                    self.errors.append(
                        f"Failed to parse motion config {config_path}: {e}"
                    )
        
        print()
    
    def verify_bvh_files(self):
        """Verify all BVH files referenced in configs exist."""
        print("Checking BVH motion files...")
        
        for motion_name, config_path in self.motion_configs.items():
            if not os.path.exists(config_path):
                continue  # Already reported in previous check
            
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                bvh_path = config.get('filepath')
                if not bvh_path:
                    self.errors.append(
                        f"Motion config {config_path} missing 'filepath' field"
                    )
                    continue
                
                if not os.path.exists(bvh_path):
                    self.errors.append(
                        f"BVH file not found: {bvh_path} (referenced by '{motion_name}')"
                    )
                else:
                    # Check file size
                    file_size = os.path.getsize(bvh_path)
                    if file_size == 0:
                        self.errors.append(
                            f"BVH file is empty: {bvh_path}"
                        )
                    else:
                        self.successes.append(
                            f"✓ BVH file '{motion_name}': {bvh_path} ({file_size:,} bytes)"
                        )
            except Exception as e:
                self.errors.append(
                    f"Failed to verify BVH for motion '{motion_name}': {e}"
                )
        
        print()
    
    def verify_theme_motion_consistency(self):
        """Verify theme-motion mappings are consistent between services."""
        print("Checking theme-motion mapping consistency...")
        
        # Check if both services have the same themes
        anim_themes = set(self.theme_motions_anim.keys())
        theme_themes = set(self.theme_motions_theme.keys())
        
        if anim_themes != theme_themes:
            missing_in_anim = theme_themes - anim_themes
            missing_in_theme = anim_themes - theme_themes
            
            if missing_in_anim:
                self.errors.append(
                    f"Themes in ThemeManager but not AnimationEngine: {missing_in_anim}"
                )
            if missing_in_theme:
                self.errors.append(
                    f"Themes in AnimationEngine but not ThemeManager: {missing_in_theme}"
                )
        else:
            self.successes.append(
                f"✓ Both services define the same {len(anim_themes)} themes"
            )
        
        # Check if motion lists are identical for each theme
        for theme in anim_themes & theme_themes:
            anim_motions = set(self.theme_motions_anim[theme])
            theme_motions = set(self.theme_motions_theme[theme])
            
            if anim_motions != theme_motions:
                self.errors.append(
                    f"Theme '{theme}' has different motions in services:\n"
                    f"  AnimationEngine: {sorted(anim_motions)}\n"
                    f"  ThemeManager: {sorted(theme_motions)}"
                )
            else:
                self.successes.append(
                    f"✓ Theme '{theme}': {len(anim_motions)} motions consistent"
                )
        
        print()
    
    def verify_motion_references(self):
        """Verify all motions referenced in theme mappings exist in MOTION_CONFIGS."""
        print("Checking motion references...")
        
        all_referenced_motions = set()
        for theme, motions in self.theme_motions_anim.items():
            all_referenced_motions.update(motions)
        
        defined_motions = set(self.motion_configs.keys())
        
        # Check for undefined motions
        undefined = all_referenced_motions - defined_motions
        if undefined:
            self.errors.append(
                f"Motions referenced in themes but not defined in MOTION_CONFIGS: {undefined}"
            )
        else:
            self.successes.append(
                f"✓ All {len(all_referenced_motions)} referenced motions are defined"
            )
        
        # Check for unused motions
        unused = defined_motions - all_referenced_motions
        if unused:
            self.warnings.append(
                f"Motions defined but not used in any theme: {unused}"
            )
        
        print()
    
    def verify_theme_coverage(self):
        """Verify all expected themes have motion mappings."""
        print("Checking theme coverage...")
        
        expected_themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
        defined_themes = set(self.theme_motions_anim.keys())
        
        missing_themes = set(expected_themes) - defined_themes
        if missing_themes:
            self.errors.append(
                f"Expected themes missing from configuration: {missing_themes}"
            )
        else:
            self.successes.append(
                f"✓ All {len(expected_themes)} expected themes are configured"
            )
        
        # Check each theme has at least one motion
        for theme in expected_themes:
            if theme in self.theme_motions_anim:
                motions = self.theme_motions_anim[theme]
                if not motions:
                    self.errors.append(
                        f"Theme '{theme}' has no motions defined"
                    )
                else:
                    self.successes.append(
                        f"✓ Theme '{theme}': {len(motions)} motion(s) - {motions}"
                    )
        
        print()
    
    def print_results(self):
        """Print verification results."""
        print("=" * 70)
        print("Verification Results")
        print("=" * 70)
        print()
        
        if self.successes:
            print(f"✓ SUCCESSES ({len(self.successes)}):")
            print("-" * 70)
            for success in self.successes:
                print(f"  {success}")
            print()
        
        if self.warnings:
            print(f"⚠ WARNINGS ({len(self.warnings)}):")
            print("-" * 70)
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print(f"✗ ERRORS ({len(self.errors)}):")
            print("-" * 70)
            for error in self.errors:
                print(f"  {error}")
            print()
        
        print("=" * 70)
        if self.errors:
            print("VERIFICATION FAILED")
            print(f"Found {len(self.errors)} error(s) and {len(self.warnings)} warning(s)")
        else:
            print("VERIFICATION PASSED")
            print(f"All checks passed with {len(self.warnings)} warning(s)")
        print("=" * 70)


def print_configuration_summary():
    """Print a summary of the motion configuration."""
    print()
    print("=" * 70)
    print("Motion Configuration Summary")
    print("=" * 70)
    print()
    
    service = AnimationEngineService()
    
    print("Available Motions:")
    print("-" * 70)
    for motion_name, config_path in sorted(service.MOTION_CONFIGS.items()):
        print(f"  • {motion_name:15} → {config_path}")
    print()
    
    print("Theme-to-Motion Mapping:")
    print("-" * 70)
    for theme, motions in sorted(service.THEME_MOTIONS.items()):
        print(f"  • {theme:10} → {', '.join(motions)}")
    print()
    
    print("Motion Usage by Theme:")
    print("-" * 70)
    
    # Count how many themes use each motion
    motion_usage = {}
    for theme, motions in service.THEME_MOTIONS.items():
        for motion in motions:
            if motion not in motion_usage:
                motion_usage[motion] = []
            motion_usage[motion].append(theme)
    
    for motion, themes in sorted(motion_usage.items()):
        print(f"  • {motion:15} used by {len(themes)} theme(s): {', '.join(themes)}")
    print()


def main():
    """Main entry point."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Motion Configuration Verification Tool" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Print configuration summary
    print_configuration_summary()
    
    # Run verification
    verifier = MotionConfigVerifier()
    success = verifier.verify_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
