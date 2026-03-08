# Motion Configuration Quick Reference

## Overview

This directory contains the motion sequence configuration for the Themed Animation Platform. The configuration maps BVH motion files to themes and provides a motion selection algorithm.

## Quick Start

### View Configuration

```bash
# Run the demo to see all configurations
python3 services/demo_motion_config.py

# Verify all files and mappings
python3 services/verify_motion_config.py

# Run tests
python3 -m pytest services/test_motion_config.py -v
```

### Use in Code

```python
from services.animation_engine_service import AnimationEngineService

service = AnimationEngineService()

# Select motion for a theme
motion = service.select_motion_for_theme('jungle')
# Returns one of: 'zombie', 'jumping', 'wave_hello'

# Animate a drawing with theme-appropriate motion
animation_data = service.animate_drawing(
    image_path="uploads/drawing.png",
    drawing_id="drawing-123",
    theme="christmas"
)
```

## File Locations

- **BVH Files**: `examples/bvh/` (fair1, rokoko, cmu1 subdirectories)
- **Motion Configs**: `examples/config/motion/*.yaml`
- **Documentation**: `services/MOTION_CONFIGURATION.md`
- **Demo Script**: `services/demo_motion_config.py`
- **Verification**: `services/verify_motion_config.py`
- **Tests**: `services/test_motion_config.py`

## Theme-Motion Mapping

| Theme     | Motions                                    |
|-----------|--------------------------------------------|
| jungle    | zombie, jumping, wave_hello                |
| christmas | jesse_dance, wave_hello, dab               |
| party     | jesse_dance, jumping, dab, jumping_jacks   |
| school    | wave_hello, jumping, dab                   |
| ocean     | wave_hello, zombie, jesse_dance            |
| general   | wave_hello, jumping, dab                   |

## Available Motions

1. **dab** - Celebratory gesture (fair1)
2. **jumping** - Vertical jumping motion (fair1)
3. **wave_hello** - Friendly waving gesture (fair1)
4. **zombie** - Slow, shuffling walk (fair1)
5. **jesse_dance** - Energetic dance routine (rokoko)
6. **jumping_jacks** - Exercise jumping jacks (cmu1)

## Configuration Files

Each motion has a YAML config file that specifies:
- BVH file path
- Frame range
- Ground plane joint
- Forward direction vectors
- Scale and up axis

## Verification Status

✅ All BVH files verified to exist
✅ All motion config files verified
✅ Theme-motion mapping consistent across services
✅ All tests passing (17/17)
✅ Motion selection algorithm working correctly

## Requirements

**Requirement 11.5**: The Theme_Manager SHALL maintain a mapping of themes to appropriate BVH motion files

This requirement is fully implemented and verified.

## For More Information

See `services/MOTION_CONFIGURATION.md` for complete documentation including:
- Detailed motion descriptions
- Algorithm implementation details
- Theme design rationale
- Extension guidelines
- Troubleshooting guide
