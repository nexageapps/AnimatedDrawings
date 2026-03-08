#!/usr/bin/env python3
"""
Motion Configuration Demo

Demonstrates the motion sequence configuration and theme-motion mapping
for the Themed Animation Platform.

Requirements: 11.5
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.animation_engine_service import AnimationEngineService
from services.theme_manager import ThemeManagerService


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(text.center(70))
    print("=" * 70)
    print()


def print_section(text):
    """Print a formatted section header."""
    print()
    print("-" * 70)
    print(text)
    print("-" * 70)


def demo_motion_configs():
    """Demonstrate available motion configurations."""
    print_header("Motion Configuration Demo")
    
    service = AnimationEngineService()
    
    print_section("Available Motion Sequences")
    print()
    print(f"Total motions configured: {len(service.MOTION_CONFIGS)}")
    print()
    
    for motion_name, config_path in sorted(service.MOTION_CONFIGS.items()):
        print(f"  • {motion_name:15} → {config_path}")
    print()


def demo_theme_mappings():
    """Demonstrate theme-to-motion mappings."""
    print_section("Theme-to-Motion Mappings")
    
    service = AnimationEngineService()
    
    print()
    print(f"Total themes configured: {len(service.THEME_MOTIONS)}")
    print()
    
    for theme, motions in sorted(service.THEME_MOTIONS.items()):
        print(f"  {theme.upper()}")
        print(f"    Motions: {', '.join(motions)}")
        print(f"    Count: {len(motions)}")
        print()


def demo_motion_selection():
    """Demonstrate motion selection for each theme."""
    print_section("Motion Selection Examples")
    
    service = AnimationEngineService()
    themes = ['jungle', 'christmas', 'party', 'school', 'ocean', 'general']
    
    print()
    print("Selecting motions for each theme (5 samples per theme):")
    print()
    
    for theme in themes:
        print(f"  {theme.upper()}:")
        selections = []
        for i in range(5):
            motion = service.select_motion_for_theme(theme)
            selections.append(motion)
        
        # Count occurrences
        motion_counts = {}
        for motion in selections:
            motion_counts[motion] = motion_counts.get(motion, 0) + 1
        
        for motion, count in sorted(motion_counts.items()):
            print(f"    • {motion}: {count} time(s)")
        print()


def demo_motion_usage_stats():
    """Demonstrate motion usage statistics."""
    print_section("Motion Usage Statistics")
    
    service = AnimationEngineService()
    
    # Count how many themes use each motion
    motion_usage = {}
    for theme, motions in service.THEME_MOTIONS.items():
        for motion in motions:
            if motion not in motion_usage:
                motion_usage[motion] = []
            motion_usage[motion].append(theme)
    
    print()
    print("Motion usage across themes:")
    print()
    
    # Sort by usage count (descending)
    sorted_motions = sorted(motion_usage.items(), 
                           key=lambda x: len(x[1]), 
                           reverse=True)
    
    for motion, themes in sorted_motions:
        print(f"  {motion:15} used by {len(themes)} theme(s): {', '.join(themes)}")
    print()


def demo_theme_characteristics():
    """Demonstrate theme characteristics and design rationale."""
    print_section("Theme Characteristics")
    
    theme_descriptions = {
        'jungle': {
            'description': 'Animal-like and explorer movements',
            'rationale': 'Slow lurching (zombie), energetic jumping, friendly gestures'
        },
        'christmas': {
            'description': 'Festive and celebratory motions',
            'rationale': 'Dancing, waving, modern celebratory gestures'
        },
        'party': {
            'description': 'High-energy celebratory movements',
            'rationale': 'Most variety with dancing, jumping, dab, jumping jacks'
        },
        'school': {
            'description': 'Educational and playful motions',
            'rationale': 'Friendly greetings, playful jumping, student gestures'
        },
        'ocean': {
            'description': 'Swimming and floating-like movements',
            'rationale': 'Waving (water-themed), slow floating, fluid dancing'
        },
        'general': {
            'description': 'Default general-purpose motions',
            'rationale': 'Universal friendly gestures and common movements'
        }
    }
    
    service = AnimationEngineService()
    
    print()
    for theme in sorted(theme_descriptions.keys()):
        info = theme_descriptions[theme]
        motions = service.THEME_MOTIONS[theme]
        
        print(f"  {theme.upper()}")
        print(f"    Description: {info['description']}")
        print(f"    Motions: {', '.join(motions)}")
        print(f"    Rationale: {info['rationale']}")
        print()


def demo_consistency_check():
    """Demonstrate consistency between services."""
    print_section("Service Consistency Check")
    
    anim_service = AnimationEngineService()
    theme_service = ThemeManagerService()
    
    print()
    print("Checking consistency between AnimationEngineService and ThemeManagerService...")
    print()
    
    # Check themes
    anim_themes = set(anim_service.THEME_MOTIONS.keys())
    theme_themes = set(theme_service.THEME_MOTIONS.keys())
    
    if anim_themes == theme_themes:
        print(f"  ✓ Both services define the same {len(anim_themes)} themes")
    else:
        print(f"  ✗ Theme sets differ!")
        print(f"    AnimationEngine: {sorted(anim_themes)}")
        print(f"    ThemeManager: {sorted(theme_themes)}")
    
    # Check motion mappings
    all_consistent = True
    for theme in anim_themes & theme_themes:
        anim_motions = set(anim_service.THEME_MOTIONS[theme])
        theme_motions = set(theme_service.THEME_MOTIONS[theme])
        
        if anim_motions == theme_motions:
            print(f"  ✓ Theme '{theme}': {len(anim_motions)} motions consistent")
        else:
            print(f"  ✗ Theme '{theme}': motions differ!")
            all_consistent = False
    
    print()
    if all_consistent and anim_themes == theme_themes:
        print("  ✓ ALL CHECKS PASSED - Configuration is consistent!")
    else:
        print("  ✗ INCONSISTENCIES FOUND - Please review configuration!")
    print()


def demo_invalid_theme_fallback():
    """Demonstrate fallback behavior for invalid themes."""
    print_section("Invalid Theme Fallback")
    
    service = AnimationEngineService()
    invalid_themes = ['invalid', 'nonexistent', 'test', 'unknown']
    
    print()
    print("Testing fallback behavior for invalid themes:")
    print()
    
    general_motions = set(service.THEME_MOTIONS['general'])
    
    for invalid_theme in invalid_themes:
        motion = service.select_motion_for_theme(invalid_theme)
        is_general = motion in general_motions
        status = "✓" if is_general else "✗"
        print(f"  {status} Theme '{invalid_theme}' → motion '{motion}' "
              f"({'general theme' if is_general else 'ERROR'})")
    
    print()
    print(f"  All invalid themes fall back to general motions: {', '.join(general_motions)}")
    print()


def main():
    """Main entry point."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "Motion Configuration Demo" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run all demos
    demo_motion_configs()
    demo_theme_mappings()
    demo_motion_selection()
    demo_motion_usage_stats()
    demo_theme_characteristics()
    demo_consistency_check()
    demo_invalid_theme_fallback()
    
    print()
    print("=" * 70)
    print("Demo Complete".center(70))
    print("=" * 70)
    print()
    print("For more information, see:")
    print("  • services/MOTION_CONFIGURATION.md")
    print("  • services/verify_motion_config.py")
    print("  • services/test_motion_config.py")
    print()


if __name__ == '__main__':
    main()
