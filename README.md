# Themed Animation Platform

A multi-user platform that transforms static drawings into animated characters within shared, themed virtual worlds. Built on top of [Facebook Research's AnimatedDrawings](https://github.com/facebookresearch/AnimatedDrawings) library.

## Overview

The Themed Animation Platform accepts drawing images, automatically animates them using AI-powered character detection, and places them into collaborative themed environments where multiple users' creations coexist and interact spatially.

### Key Features

- **Email-based submission workflow** - Send drawings via email with theme specifications
- **AI-powered animation** - Automatic character detection and animation using Facebook's Animated Drawings
- **Themed virtual worlds** - Shared environments (jungle, christmas, party, school, ocean) where drawings come together
- **Intelligent spatial positioning** - Smart placement with collision avoidance and theme-aware rules
- **Multi-user collaboration** - Multiple users' drawings coexist in the same themed world
- **Dual operation modes** - Testing mode for development, production mode for email-based workflow

## Acknowledgments

This project is built on top of the excellent work by Facebook Research:

- **Original Project:** [AnimatedDrawings](https://github.com/facebookresearch/AnimatedDrawings)
- **Research Paper:** [A Method for Animating Children's Drawings of the Human Figure](https://dl.acm.org/doi/10.1145/3592788)
- **Authors:** Harrison Jesse Smith, Qingyuan Zheng, Yifei Li, Somya Jain, Jessica K. Hodgins
- **License:** MIT License

We are grateful to the Facebook Research team for making this technology available to the community.

## Quick Start

### Prerequisites

- Python 3.8.13 or higher (tested with Python 3.12.4)
- PostgreSQL 12+ (for production)
- Redis (for caching and job queue)
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd AnimatedDrawings
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Create PostgreSQL database
createdb themed_animations

# Run migrations
python database/migrate.py
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Run the application:
```bash
# Testing mode (direct upload, no email required)
./run_testing.sh

# Production mode (email-based workflow)
./run_production.sh
```

7. Open your browser:
```
http://localhost:5001
```

## How It Works

### User Workflow

1. **Submit Drawing** - Send an email with your drawing attachment and theme keyword (e.g., "jungle", "christmas")
2. **Automatic Processing** - System detects character, generates segmentation, and applies theme-appropriate animation
3. **World Placement** - Drawing is intelligently placed in a shared themed world with other users' creations
4. **Notification** - Receive email with link to view your animated drawing in the themed world

### System Architecture

The platform consists of six core services:

- **Email Receiver Service** - Monitors inbox, extracts attachments, parses themes
- **Image Processing Service** - Validates, normalizes, and stores images
- **Animation Engine Service** - Integrates Facebook Animated Drawings for character detection and animation
- **World Compositor Service** - Manages themed worlds and spatial positioning with collision avoidance
- **Rendering Service** - Composes scenes, synchronizes animations, generates video output
- **Notification Service** - Sends confirmation emails with world viewing URLs

### Supported Themes

- **Jungle** - Adventure theme with ground-based positioning and nature animations
- **Christmas** - Festive theme with clustered positioning and celebratory motions
- **Party** - Celebration theme with random distribution and energetic animations
- **School** - Educational theme with structured row-based positioning
- **Ocean** - Underwater theme with depth-based layers and swimming motions
- **General** - Default theme with balanced grid distribution

## 📁 Project Structure

```
AnimatedDrawings/
├── app.py                      # Flask web application
├── templates/
│   └── index.html             # Main UI template
├── static/
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend logic
├── test_images/               # Sample images for testing
├── uploads/                   # User uploaded images
├── animated_drawings/         # Core animation library (Facebook Research)
├── examples/                  # Example configurations and BVH files
├── README.md                  # This file
└── README_ORIGINAL.md         # Original Facebook Research README
```

## 🧪 Testing

### Add Test Images

Place your test images in the `test_images/` folder:

```bash
cp your_drawing.png test_images/
```

The web UI will automatically detect and display them in Testing Mode.

### Run Example Animation

```bash
source venv/bin/activate
python test_animation.py
```

## 🔧 Configuration

### Environment Variables

- `APP_MODE`: Set to `testing` or `production` (default: `testing`)
- `PORT`: Server port (default: `5000`)

### Example:

```bash
# Run in production mode on port 8080
APP_MODE=production PORT=8080 python app.py
```

## 📚 Original Documentation

For detailed information about the underlying AnimatedDrawings technology, configuration files, BVH motion files, and advanced features, please refer to:

- **[README_ORIGINAL.md](README_ORIGINAL.md)** - Complete original documentation
- **[examples/config/README.md](examples/config/README.md)** - Configuration file documentation

## 🎨 How It Works

1. **Upload/Select Drawing:** Choose a drawing in Testing or Production mode
2. **Character Detection:** AI detects the human figure in the drawing
3. **Pose Estimation:** Identifies joint locations (head, arms, legs, etc.)
4. **Rigging:** Creates a skeleton structure for animation
5. **Motion Retargeting:** Applies BVH motion data to the character
6. **Animation Output:** Generates animated GIF or MP4

## 🛠️ Development

### Project Status

This is an active development project. Current features:
- ✅ Web UI with Testing/Production modes
- ✅ File upload system
- ✅ Mode switching interface
- 🚧 Animation pipeline integration (in progress)
- 🚧 Real-time preview
- 🚧 Multiple character support

### Contributing

Contributions are welcome! Please ensure you:
1. Acknowledge the original Facebook Research project
2. Follow the existing code style
3. Test in both Testing and Production modes
4. Update documentation as needed

## 📄 License

This project maintains the MIT License from the original AnimatedDrawings project.

**Original License:** [LICENSE](LICENSE) - Facebook Research AnimatedDrawings

## 🔗 Links

- **Original Project:** https://github.com/facebookresearch/AnimatedDrawings
- **Research Paper:** https://dl.acm.org/doi/10.1145/3592788
- **Demo Website:** https://sketch.metademolab.com/

## 📞 Support

For issues related to:
- **Web UI:** Open an issue in this repository
- **Core Animation:** Refer to the [original project](https://github.com/facebookresearch/AnimatedDrawings)

## 🎓 Citation

If you use this project in your research, please cite the original paper:

```bibtex
@article{10.1145/3592788,
author = {Smith, Harrison Jesse and Zheng, Qingyuan and Li, Yifei and Jain, Somya and Hodgins, Jessica K.},
title = {A Method for Animating Children's Drawings of the Human Figure},
year = {2023},
publisher = {Association for Computing Machinery},
volume = {42},
number = {3},
journal = {ACM Trans. Graph.},
articleno = {32},
numpages = {15}
}
```

---

**Built with ❤️ on top of Facebook Research's AnimatedDrawings**
