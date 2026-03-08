# Animation Engine Service

The Animation Engine Service integrates with Facebook's Animated Drawings library to automatically animate static drawings. It provides character detection, segmentation, skeleton rigging, and theme-aware motion application.

## Features

- **Character Detection**: Automatically detects drawn humanoids in images using pre-trained models
- **Segmentation**: Generates segmentation masks to separate characters from backgrounds
- **Skeleton Rigging**: Creates joint annotations and skeleton structure for animation
- **Theme-Aware Motion Selection**: Selects appropriate motion sequences based on theme context
- **Animation Rendering**: Applies BVH motion files and renders animated GIFs
- **Storage Integration**: Exports animations to configurable storage backends

## Requirements

### System Requirements

- Python 3.8+
- TorchServe running with Animated Drawings models
- OpenCV (cv2)
- NumPy
- SciPy
- scikit-image
- PyYAML
- requests

### TorchServe Setup

The Animation Engine requires TorchServe to be running with two models:
1. `drawn_humanoid_detector` - Detects characters in drawings
2. `drawn_humanoid_pose_estimator` - Estimates skeleton keypoints

See the main README for TorchServe setup instructions.

## Architecture

### Service Components

```
AnimationEngineService
├── detect_character()        # Character detection using TorchServe
├── generate_segmentation()   # Mask and skeleton generation
├── select_motion_for_theme() # Theme-aware motion selection
├── apply_motion()            # Motion application and rendering
├── export_animation()        # Storage export
└── animate_drawing()         # Complete pipeline
```

### Data Flow

```
Input Image
    ↓
Character Detection (TorchServe)
    ↓
Segmentation & Skeleton Generation
    ↓
Theme-Based Motion Selection
    ↓
Motion Application & Rendering
    ↓
Export to Storage
    ↓
AnimationData Output
```

## Usage

### Basic Usage

```python
from services.animation_engine_service import AnimationEngineService
from services.storage_service import LocalStorageService

# Initialize service
storage = LocalStorageService(base_path="uploads")
animation_service = AnimationEngineService(
    storage_service=storage,
    work_dir="uploads/animations"
)

# Animate a drawing
animation_data = animation_service.animate_drawing(
    image_path="path/to/drawing.png",
    drawing_id="drawing-123",
    theme="jungle"
)

print(f"Animation URL: {animation_data.animation_file_url}")
print(f"Motion used: {animation_data.motion_sequence}")
```

### Step-by-Step Pipeline

```python
# Step 1: Detect character
detection = animation_service.detect_character("drawing.png")
if not detection.success:
    print(f"Detection failed: {detection.error_message}")
    return

print(f"Detected with confidence: {detection.confidence}")
print(f"Bounding box: {detection.bbox}")

# Step 2: Generate segmentation
segmentation = animation_service.generate_segmentation(
    "drawing.png", 
    detection, 
    "output_dir"
)

if not segmentation.success:
    print(f"Segmentation failed: {segmentation.error_message}")
    return

print(f"Mask path: {segmentation.mask_path}")
print(f"Skeleton joints: {len(segmentation.skeleton_data['skeleton'])}")

# Step 3: Select motion
motion = animation_service.select_motion_for_theme("jungle")
print(f"Selected motion: {motion}")

# Step 4: Apply motion
animation = animation_service.apply_motion("output_dir", motion)
if not animation.success:
    print(f"Animation failed: {animation.error_message}")
    return

print(f"Animation path: {animation.animation_path}")

# Step 5: Export
animation_url = animation_service.export_animation(
    animation.animation_path,
    "drawing-123"
)
print(f"Exported to: {animation_url}")
```

### Demo Script

Run the included demo script:

```bash
# Activate virtual environment
source venv/bin/activate

# Run demo
python services/demo_animation_engine.py test_images/garlic.png jungle
```

## Theme-Motion Mapping

The service maps themes to appropriate motion sequences:

| Theme | Available Motions |
|-------|------------------|
| jungle | zombie, jumping, wave_hello |
| christmas | jesse_dance, wave_hello, dab |
| party | jesse_dance, jumping, dab, jumping_jacks |
| school | wave_hello, jumping, dab |
| ocean | wave_hello, zombie, jesse_dance |
| general | wave_hello, jumping, dab |

Motion sequences are randomly selected from the theme's available motions.

## API Reference

### AnimationEngineService

#### `__init__(storage_service, work_dir)`

Initialize the animation engine service.

**Parameters:**
- `storage_service` (StorageService, optional): Storage backend for outputs
- `work_dir` (str): Working directory for temporary files

#### `detect_character(image_path) -> CharacterDetection`

Detect character in drawing using TorchServe.

**Parameters:**
- `image_path` (str): Path to drawing image

**Returns:**
- `CharacterDetection`: Detection result with bbox and confidence

**Requirements:** 3.1

#### `generate_segmentation(image_path, detection, output_dir) -> SegmentationResult`

Generate segmentation mask and skeleton annotations.

**Parameters:**
- `image_path` (str): Path to original image
- `detection` (CharacterDetection): Detection result with bbox
- `output_dir` (str): Directory to save outputs

**Returns:**
- `SegmentationResult`: Segmentation result with paths and skeleton data

**Requirements:** 3.2

#### `select_motion_for_theme(theme) -> str`

Select appropriate motion sequence based on theme.

**Parameters:**
- `theme` (str): Theme name

**Returns:**
- `str`: Motion sequence name

**Requirements:** 11.1, 11.2, 11.3, 11.4

#### `apply_motion(char_anno_dir, motion_sequence, retarget_cfg) -> AnimationResult`

Apply motion sequence to character and generate animation.

**Parameters:**
- `char_anno_dir` (str): Directory with character annotations
- `motion_sequence` (str): Name of motion sequence
- `retarget_cfg` (str, optional): Retarget config path

**Returns:**
- `AnimationResult`: Animation result with file path

**Requirements:** 3.4, 3.5

#### `export_animation(animation_path, drawing_id) -> str`

Export animation to storage.

**Parameters:**
- `animation_path` (str): Path to animation file
- `drawing_id` (str): Drawing ID for organizing storage

**Returns:**
- `str`: Storage path/URL

#### `animate_drawing(image_path, drawing_id, theme) -> AnimationData`

Complete animation pipeline for a drawing.

**Parameters:**
- `image_path` (str): Path to drawing image
- `drawing_id` (str): Drawing ID
- `theme` (str): Theme name for motion selection

**Returns:**
- `AnimationData`: Complete animation data

**Raises:**
- `ValueError`: If animation fails

**Requirements:** 3.1, 3.2, 3.4, 3.5, 11.1, 11.2, 11.3, 11.4

### Data Classes

#### CharacterDetection

```python
@dataclass
class CharacterDetection:
    success: bool
    confidence: float = 0.0
    bbox: Optional[Tuple[int, int, int, int]] = None
    error_message: Optional[str] = None
```

#### SegmentationResult

```python
@dataclass
class SegmentationResult:
    success: bool
    mask_path: Optional[str] = None
    skeleton_data: Optional[Dict] = None
    cropped_image_path: Optional[str] = None
    error_message: Optional[str] = None
```

#### AnimationResult

```python
@dataclass
class AnimationResult:
    success: bool
    animation_path: Optional[str] = None
    motion_sequence: Optional[str] = None
    error_message: Optional[str] = None
```

## Output Files

The animation pipeline generates several output files:

### Working Directory Structure

```
uploads/animations/{drawing_id}/
├── image.png              # Original image
├── bounding_box.yaml      # Character bounding box
├── texture.png            # Cropped character (RGBA)
├── mask.png               # Segmentation mask
├── char_cfg.yaml          # Character configuration
├── joint_overlay.png      # Skeleton visualization
├── mvc_cfg.yaml           # MVC configuration
└── video.gif              # Animated output
```

### Storage Structure

```
uploads/
├── animations/
│   └── {drawing_id}/
│       └── video.gif      # Exported animation
└── masks/
    └── {drawing_id}/
        └── mask.png       # Exported mask
```

## Error Handling

The service provides detailed error handling:

### Character Detection Errors

- Image not found or corrupted
- No characters detected in image
- TorchServe connection errors
- Invalid image format

### Segmentation Errors

- Pose estimation failures
- No skeleton detected
- Multiple skeletons detected
- Segmentation processing errors

### Animation Errors

- Invalid motion sequence
- Missing configuration files
- Rendering failures
- Export failures

All errors are logged and returned in result objects with descriptive error messages.

## Testing

Run the test suite:

```bash
source venv/bin/activate
python -m pytest services/test_animation_engine.py -v
```

### Test Coverage

- Motion selection for all themes
- Character detection with various inputs
- Skeleton building and structure
- Segmentation mask generation
- Animation export
- Error handling scenarios
- Data class validation

## Performance Considerations

### Processing Time

Typical processing times per drawing:
- Character detection: 1-3 seconds
- Segmentation: 2-5 seconds
- Animation rendering: 5-15 seconds
- Total: 8-23 seconds per drawing

### Resource Usage

- Memory: ~500MB-1GB per concurrent animation
- CPU: Intensive during rendering
- Network: TorchServe API calls

### Optimization Tips

1. **Batch Processing**: Process multiple drawings in parallel
2. **Image Preprocessing**: Resize large images before processing
3. **Caching**: Cache detection results for retry scenarios
4. **Resource Limits**: Limit concurrent animations based on available resources

## Integration with Other Services

### Theme Manager Integration

```python
from services.theme_manager import ThemeManagerService
from services.animation_engine_service import AnimationEngineService

theme_manager = ThemeManagerService()
animation_service = AnimationEngineService()

# Get theme and select motion
theme = theme_manager.get_theme('jungle')
motion = animation_service.select_motion_for_theme(theme.name)
```

### Storage Service Integration

```python
from services.storage_service import LocalStorageService
from services.animation_engine_service import AnimationEngineService

storage = LocalStorageService(base_path="uploads")
animation_service = AnimationEngineService(storage_service=storage)

# Animations are automatically stored using the storage service
animation_data = animation_service.animate_drawing(
    image_path="drawing.png",
    drawing_id="123",
    theme="party"
)
```

### Database Integration

```python
from database.orm import AnimationData as AnimationDataORM, get_session
from services.animation_engine_service import AnimationEngineService

animation_service = AnimationEngineService()

# Generate animation
animation_data = animation_service.animate_drawing(
    image_path="drawing.png",
    drawing_id="123",
    theme="ocean"
)

# Save to database
session = get_session()
try:
    animation_orm = AnimationDataORM(
        id=animation_data.id,
        drawing_id=animation_data.drawing_id,
        character_detected=animation_data.character_detected,
        segmentation_mask_url=animation_data.segmentation_mask_url,
        skeleton_data=animation_data.skeleton_data,
        motion_sequence=animation_data.motion_sequence,
        animation_file_url=animation_data.animation_file_url,
        sprite_sheet_url=animation_data.sprite_sheet_url
    )
    session.add(animation_orm)
    session.commit()
finally:
    session.close()
```

## Troubleshooting

### TorchServe Connection Errors

**Problem:** `Network error: Connection refused`

**Solution:**
1. Verify TorchServe is running: `curl http://localhost:8080/ping`
2. Check models are loaded: `curl http://localhost:8081/models`
3. Restart TorchServe if needed

### No Character Detected

**Problem:** `No drawn humanoids detected in image`

**Solution:**
1. Ensure drawing has a clear humanoid character
2. Check image quality and resolution
3. Try with a different drawing
4. Verify TorchServe models are working

### Segmentation Failures

**Problem:** `No skeleton detected in character bounding box`

**Solution:**
1. Check character is fully visible in bounding box
2. Ensure character has clear limbs and joints
3. Try adjusting image contrast/brightness
4. Verify pose estimation model is loaded

### Animation Rendering Errors

**Problem:** `Animation rendering completed but output file not found`

**Solution:**
1. Check disk space availability
2. Verify write permissions in work directory
3. Check for errors in animated_drawings library logs
4. Ensure motion config files exist

## Credits

This service integrates with [Facebook's Animated Drawings](https://github.com/facebookresearch/AnimatedDrawings) library.

## License

This service is part of the Themed Animation Platform and follows the same license as the main project.
