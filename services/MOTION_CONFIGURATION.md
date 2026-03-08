# Motion Sequence Configuration for Themed Animation Platform

## Overview

This document describes the motion sequence configuration for the Themed Animation Platform, including the mapping of BVH motion files to themes, file locations, and the motion selection algorithm.

**Requirements:** 11.5 - The Theme_Manager SHALL maintain a mapping of themes to appropriate BVH motion files

## Motion File Locations

All BVH motion files are stored in the `examples/bvh/` directory, organized by source:

```
examples/bvh/
├── fair1/          # Facebook AI Research motion files
│   ├── dab.bvh
│   ├── jumping.bvh
│   ├── wave_hello.bvh
│   └── zombie.bvh
├── rokoko/         # Rokoko motion capture files
│   └── jesse_dance.bvh
└── cmu1/           # Carnegie Mellon University motion files
    └── jumping_jacks.bvh
```

## Motion Configuration Files

Each motion has a corresponding YAML configuration file in `examples/config/motion/`:

```
examples/config/motion/
├── dab.yaml
├── jesse_dance.yaml
├── jumping_jacks.yaml
├── jumping.yaml
├── wave_hello.yaml
└── zombie.yaml
```

These configuration files specify:
- **filepath**: Path to the BVH file
- **start_frame_idx**: Starting frame for the motion
- **end_frame_idx**: Ending frame (null for full motion)
- **groundplane_joint**: Joint used for ground plane alignment
- **forward_perp_joint_vectors**: Joint pairs for forward direction
- **scale**: Scaling factor for the motion
- **up**: Up axis direction (+y or +z)

## Theme-to-Motion Mapping

The platform maintains a mapping of themes to appropriate motion sequences. This mapping is defined in both `ThemeManagerService` and `AnimationEngineService` for consistency.

### Mapping Table

| Theme     | Motion Sequences                                    | Description                          |
|-----------|-----------------------------------------------------|--------------------------------------|
| jungle    | zombie, jumping, wave_hello                         | Animal-like and explorer movements   |
| christmas | jesse_dance, wave_hello, dab                        | Festive and celebratory motions      |
| party     | jesse_dance, jumping, dab, jumping_jacks            | High-energy celebratory movements    |
| school    | wave_hello, jumping, dab                            | Educational and playful motions      |
| ocean     | wave_hello, zombie, jesse_dance                     | Swimming and floating-like movements |
| general   | wave_hello, jumping, dab                            | Default general-purpose motions      |

### Motion Descriptions

#### dab
- **Source**: Facebook AI Research (fair1)
- **Duration**: 339 frames
- **Character**: Celebratory gesture
- **Themes**: christmas, party, school, general
- **BVH File**: `examples/bvh/fair1/dab.bvh`

#### jumping
- **Source**: Facebook AI Research (fair1)
- **Duration**: Full motion
- **Character**: Vertical jumping motion
- **Themes**: jungle, party, school, general
- **BVH File**: `examples/bvh/fair1/jumping.bvh`

#### wave_hello
- **Source**: Facebook AI Research (fair1)
- **Duration**: Full motion
- **Character**: Friendly waving gesture
- **Themes**: jungle, christmas, school, ocean, general
- **BVH File**: `examples/bvh/fair1/wave_hello.bvh`

#### zombie
- **Source**: Facebook AI Research (fair1)
- **Duration**: Full motion
- **Character**: Slow, shuffling walk
- **Themes**: jungle, ocean
- **BVH File**: `examples/bvh/fair1/zombie.bvh`

#### jesse_dance
- **Source**: Rokoko motion capture
- **Duration**: Full motion
- **Character**: Energetic dance routine
- **Themes**: christmas, party, ocean
- **BVH File**: `examples/bvh/rokoko/jesse_dance.bvh`

#### jumping_jacks
- **Source**: Carnegie Mellon University (cmu1)
- **Duration**: 125 frames
- **Character**: Exercise jumping jacks
- **Themes**: party
- **BVH File**: `examples/bvh/cmu1/jumping_jacks.bvh`

## Motion Selection Algorithm

The motion selection algorithm is implemented in `AnimationEngineService.select_motion_for_theme()`:

### Algorithm Steps

1. **Theme Lookup**: Retrieve the list of motion sequences for the specified theme
2. **Fallback Handling**: If theme is invalid or not found, use the 'general' theme motions
3. **Random Selection**: Randomly select one motion from the theme's motion list
4. **Return**: Return the selected motion sequence name

### Implementation

```python
def select_motion_for_theme(self, theme: str) -> str:
    """
    Select appropriate motion sequence based on theme.
    
    Args:
        theme: Theme name (jungle, christmas, party, school, ocean, general)
        
    Returns:
        Motion sequence name
    """
    motions = self.THEME_MOTIONS.get(theme, self.THEME_MOTIONS['general'])
    selected = random.choice(motions)
    logger.info(f"Selected motion '{selected}' for theme '{theme}'")
    return selected
```

### Selection Characteristics

- **Random**: Each animation gets a random motion from the theme's set
- **Variety**: Multiple motions per theme ensure visual diversity
- **Contextual**: Motions are thematically appropriate for each theme
- **Fallback**: Invalid themes default to 'general' theme motions
- **Deterministic Pool**: The pool of motions is fixed per theme

## Configuration Consistency

The theme-motion mapping is maintained in two locations for consistency:

### 1. ThemeManagerService (`services/theme_manager.py`)

```python
THEME_MOTIONS = {
    'jungle': ['zombie', 'jumping', 'wave_hello'],
    'christmas': ['jesse_dance', 'wave_hello', 'dab'],
    'party': ['jesse_dance', 'jumping', 'dab', 'jumping_jacks'],
    'school': ['wave_hello', 'jumping', 'dab'],
    'ocean': ['wave_hello', 'zombie', 'jesse_dance'],
    'general': ['wave_hello', 'jumping', 'dab']
}
```

### 2. AnimationEngineService (`services/animation_engine_service.py`)

```python
THEME_MOTIONS = {
    'jungle': ['zombie', 'jumping', 'wave_hello'],
    'christmas': ['jesse_dance', 'wave_hello', 'dab'],
    'party': ['jesse_dance', 'jumping', 'dab', 'jumping_jacks'],
    'school': ['wave_hello', 'jumping', 'dab'],
    'ocean': ['wave_hello', 'zombie', 'jesse_dance'],
    'general': ['wave_hello', 'jumping', 'dab']
}
```

### 3. Motion Config Paths

```python
MOTION_CONFIGS = {
    'dab': 'examples/config/motion/dab.yaml',
    'jumping': 'examples/config/motion/jumping.yaml',
    'wave_hello': 'examples/config/motion/wave_hello.yaml',
    'zombie': 'examples/config/motion/zombie.yaml',
    'jesse_dance': 'examples/config/motion/jesse_dance.yaml',
    'jumping_jacks': 'examples/config/motion/jumping_jacks.yaml'
}
```

## File Verification

All required motion files have been verified to exist:

### BVH Files
- ✅ `examples/bvh/fair1/dab.bvh`
- ✅ `examples/bvh/fair1/jumping.bvh`
- ✅ `examples/bvh/fair1/wave_hello.bvh`
- ✅ `examples/bvh/fair1/zombie.bvh`
- ✅ `examples/bvh/rokoko/jesse_dance.bvh`
- ✅ `examples/bvh/cmu1/jumping_jacks.bvh`

### Configuration Files
- ✅ `examples/config/motion/dab.yaml`
- ✅ `examples/config/motion/jumping.yaml`
- ✅ `examples/config/motion/wave_hello.yaml`
- ✅ `examples/config/motion/zombie.yaml`
- ✅ `examples/config/motion/jesse_dance.yaml`
- ✅ `examples/config/motion/jumping_jacks.yaml`

## Usage Examples

### Selecting Motion for a Theme

```python
from services.animation_engine_service import AnimationEngineService

service = AnimationEngineService()

# Select motion for jungle theme
motion = service.select_motion_for_theme('jungle')
# Returns one of: 'zombie', 'jumping', 'wave_hello'

# Select motion for party theme
motion = service.select_motion_for_theme('party')
# Returns one of: 'jesse_dance', 'jumping', 'dab', 'jumping_jacks'

# Invalid theme falls back to general
motion = service.select_motion_for_theme('invalid_theme')
# Returns one of: 'wave_hello', 'jumping', 'dab'
```

### Complete Animation Pipeline

```python
from services.animation_engine_service import AnimationEngineService

service = AnimationEngineService()

# Animate drawing with theme-appropriate motion
animation_data = service.animate_drawing(
    image_path="uploads/drawing.png",
    drawing_id="drawing-123",
    theme="christmas"
)

# The service automatically:
# 1. Detects the character
# 2. Generates segmentation
# 3. Selects a motion from ['jesse_dance', 'wave_hello', 'dab']
# 4. Applies the motion
# 5. Renders the animation
# 6. Exports to storage

print(f"Motion used: {animation_data.motion_sequence}")
```

## Theme Design Rationale

### Jungle Theme
- **zombie**: Slow, lurching movement suitable for jungle creatures
- **jumping**: Energetic movement for playful animals
- **wave_hello**: Friendly gesture for explorer characters

### Christmas Theme
- **jesse_dance**: Festive dancing motion
- **wave_hello**: Friendly holiday greeting
- **dab**: Modern celebratory gesture

### Party Theme
- **jesse_dance**: High-energy dance routine
- **jumping**: Excited jumping motion
- **dab**: Celebratory gesture
- **jumping_jacks**: Exercise/party energy

### School Theme
- **wave_hello**: Friendly classroom greeting
- **jumping**: Playful recess activity
- **dab**: Modern student gesture

### Ocean Theme
- **wave_hello**: Waving motion (water-themed)
- **zombie**: Slow movement resembling floating/swimming
- **jesse_dance**: Fluid dance-like movement

### General Theme
- **wave_hello**: Universal friendly gesture
- **jumping**: Common energetic motion
- **dab**: Popular modern gesture

## Extending the Configuration

To add new motions or themes:

### Adding a New Motion

1. **Add BVH file** to appropriate directory in `examples/bvh/`
2. **Create config file** in `examples/config/motion/` with:
   - filepath to BVH
   - frame indices
   - groundplane joint
   - forward vectors
   - scale and up axis
3. **Update MOTION_CONFIGS** in `AnimationEngineService`
4. **Add to theme mappings** as appropriate

### Adding a New Theme

1. **Update THEME_MOTIONS** in both:
   - `ThemeManagerService`
   - `AnimationEngineService`
2. **Select appropriate motions** from existing set
3. **Seed database** with new theme using `database/seed_themes.py`
4. **Test motion selection** for new theme

## Performance Considerations

### Motion File Loading
- Motion config files are loaded on-demand during animation
- BVH files are parsed by the animated_drawings library
- No pre-loading or caching required

### Selection Performance
- Motion selection is O(1) dictionary lookup + O(n) random choice
- Negligible performance impact (<1ms)
- No database queries required

### Memory Usage
- Motion files are not kept in memory
- Each animation loads motion independently
- No shared state between animations

## Troubleshooting

### Motion Not Found Error

**Symptom**: `Unknown motion sequence: <motion_name>`

**Cause**: Motion name not in MOTION_CONFIGS

**Solution**: Verify motion name spelling and ensure it's added to MOTION_CONFIGS

### BVH File Not Found

**Symptom**: Animation fails with file not found error

**Cause**: BVH file path in config is incorrect

**Solution**: Verify filepath in motion config YAML matches actual file location

### Invalid Theme Fallback

**Symptom**: Unexpected motion for custom theme

**Cause**: Theme not in THEME_MOTIONS mapping

**Solution**: Theme falls back to 'general' - add theme to THEME_MOTIONS if needed

## References

- **Design Document**: `.kiro/specs/themed-animation-platform/design.md`
- **Requirements**: `.kiro/specs/themed-animation-platform/requirements.md` (Requirement 11.5)
- **Animation Engine Service**: `services/animation_engine_service.py`
- **Theme Manager Service**: `services/theme_manager.py`
- **Facebook Animated Drawings**: https://github.com/facebookresearch/AnimatedDrawings

## Conclusion

The motion sequence configuration is complete and verified:

✅ All BVH motion files exist in `examples/bvh/` directory
✅ All motion config files exist in `examples/config/motion/`
✅ Theme-to-motion mapping is defined and consistent
✅ Motion selection algorithm is implemented and tested
✅ Configuration is documented and maintainable

The system is ready to apply theme-appropriate motion sequences to animated drawings.
