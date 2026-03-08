# Theme Configuration Files

This directory contains JSON configuration files for each theme in the Themed Animation Platform.

## Theme Structure

Each theme configuration file defines the following properties:

```json
{
  "name": "theme_name",              // Internal identifier (lowercase, no spaces)
  "display_name": "Theme Display",   // Human-readable name
  "background_image_url": "/static/backgrounds/theme.jpg",  // Path to background image
  "dimensions": {
    "width": 1920,                   // World width in pixels
    "height": 1080                   // World height in pixels
  },
  "max_entities": 50,                // Maximum drawings per world instance
  "positioning_rules": {             // Theme-specific positioning algorithm rules
    "type": "rule_type",
    // ... additional rule parameters
  },
  "motion_sequences": [              // Available BVH motion files for this theme
    "motion1",
    "motion2"
  ],
  "description": "Theme description"
}
```

## Available Themes

### 1. Jungle Adventure (`jungle.json`)
- **Type**: Ground-based positioning with vertical layering
- **Motions**: zombie, jumping, wave_hello
- **Style**: Lush jungle environment for animals and explorers

### 2. Christmas Celebration (`christmas.json`)
- **Type**: Clustered positioning around center
- **Motions**: jesse_dance, wave_hello, dab
- **Style**: Festive scene with floating ornaments

### 3. Party Time (`party.json`)
- **Type**: Random distribution with elevation zones
- **Motions**: jesse_dance, jumping, dab, jumping_jacks
- **Style**: Vibrant party with balloons and decorations

### 4. School Days (`school.json`)
- **Type**: Row-based structured positioning
- **Motions**: wave_hello, jumping, dab
- **Style**: Classroom or playground with organized layout

### 5. Ocean Adventure (`ocean.json`)
- **Type**: Depth-based layers for swimming
- **Motions**: wave_hello, zombie, jesse_dance
- **Style**: Underwater scene with depth zones

### 6. General (`general.json`)
- **Type**: Balanced grid distribution
- **Motions**: wave_hello, jumping, dab
- **Style**: Default theme for any drawing type

## Positioning Rule Types

### Ground-Based (`jungle`)
```json
{
  "type": "ground_based",
  "ground_level": 900,
  "min_spacing": 50,
  "vertical_layering": true,
  "depth_zones": [...]
}
```

### Clustered (`christmas`)
```json
{
  "type": "clustered",
  "center_point": [960, 540],
  "cluster_radius": 600,
  "min_spacing": 50,
  "allow_floating": true
}
```

### Random Distribution (`party`)
```json
{
  "type": "random_distribution",
  "min_spacing": 50,
  "allow_elevated": true,
  "elevation_zones": [...]
}
```

### Row-Based (`school`)
```json
{
  "type": "row_based",
  "rows": 4,
  "columns": 13,
  "row_spacing": 200,
  "column_spacing": 140,
  "start_position": [100, 300]
}
```

### Depth Layers (`ocean`)
```json
{
  "type": "depth_layers",
  "min_spacing": 50,
  "layers": [...],
  "floating": true
}
```

### Balanced Grid (`general`)
```json
{
  "type": "balanced_grid",
  "min_spacing": 50,
  "grid_step": 100,
  "balanced_distribution": true
}
```

## Motion Sequences

Motion sequences are BVH files located in `examples/bvh/` directory:

- **zombie**: Slow walking motion (fair1/zombie.bvh)
- **jumping**: Jumping motion (fair1/jumping.bvh)
- **wave_hello**: Waving gesture (fair1/wave_hello.bvh)
- **jesse_dance**: Dancing motion (rokoko/jesse_dance.bvh)
- **dab**: Dab gesture (fair1/dab.bvh)
- **jumping_jacks**: Jumping jacks exercise (cmu1/jumping_jacks.bvh)

## Adding New Themes

1. Create a new JSON file in this directory (e.g., `mytheme.json`)
2. Follow the structure shown above
3. Add a background image to `static/backgrounds/mytheme.jpg`
4. Run the seeding script: `python database/seed_themes.py`
5. Verify the theme appears in the database

## Seeding the Database

To populate the database with these theme configurations:

```bash
# From project root
python database/seed_themes.py
```

This will:
- Read all JSON files in this directory
- Create or update themes in the database
- Verify the themes were created successfully

## Requirements Mapping

- **Requirement 4.1**: Support for at least 5 themes (jungle, christmas, party, school, ocean)
- **Requirement 4.5**: Theme-specific properties including backgrounds, dimensions, and positioning rules
- **Requirement 11.5**: Theme-to-motion-sequence mapping
