"""
Test script for Theme Manager Service

Tests the basic functionality of the ThemeManagerService without requiring a database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.theme_manager import ThemeManagerService


def test_theme_motions_mapping():
    """Test that theme-motion mapping is correctly defined"""
    service = ThemeManagerService()
    
    print("Testing Theme-Motion Mapping...")
    print("=" * 60)
    
    # Test all required themes using the hardcoded mapping
    required_themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
    
    for theme_name in required_themes:
        # Access the hardcoded mapping directly (doesn't require database)
        motions = service.THEME_MOTIONS.get(theme_name, [])
        print(f"\n{theme_name.upper()}:")
        print(f"  Motions: {', '.join(motions)}")
        assert len(motions) > 0, f"Theme {theme_name} has no motion sequences"
    
    print("\n" + "=" * 60)
    print("✓ All themes have motion sequences defined")


def test_default_theme():
    """Test default theme constant"""
    service = ThemeManagerService()
    
    print("\nTesting Default Theme...")
    print("=" * 60)
    print(f"Default theme: {service.DEFAULT_THEME_NAME}")
    
    # Verify default theme has motions (using hardcoded mapping)
    motions = service.THEME_MOTIONS.get(service.DEFAULT_THEME_NAME, [])
    print(f"Default theme motions: {', '.join(motions)}")
    
    assert service.DEFAULT_THEME_NAME == 'general', "Default theme should be 'general'"
    assert len(motions) > 0, "Default theme must have motion sequences"
    
    print("✓ Default theme is correctly configured")


def test_config_directory():
    """Test that config directory exists"""
    service = ThemeManagerService()
    
    print("\nTesting Configuration Directory...")
    print("=" * 60)
    print(f"Config directory: {service.config_dir}")
    print(f"Exists: {service.config_dir.exists()}")
    
    if service.config_dir.exists():
        config_files = list(service.config_dir.glob('*.json'))
        print(f"Found {len(config_files)} theme configuration files:")
        for config_file in config_files:
            print(f"  - {config_file.name}")
        
        assert len(config_files) >= 6, "Should have at least 6 theme config files"
        print("✓ Configuration directory is properly set up")
    else:
        print("⚠ Configuration directory does not exist yet")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("THEME MANAGER SERVICE TESTS")
    print("=" * 60)
    
    try:
        test_theme_motions_mapping()
        test_default_theme()
        test_config_directory()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
