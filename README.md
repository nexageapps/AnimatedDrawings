# 🎨 Animated Drawings - Web UI Platform

A modern web-based platform for animating drawings, built on top of [Facebook Research's AnimatedDrawings](https://github.com/facebookresearch/AnimatedDrawings) project.

## 📋 Overview

This project extends the original AnimatedDrawings research by providing:
- **Web-based UI** for easy interaction
- **Testing & Production modes** for development and deployment
- **Simple file upload** interface
- **Multiple animation presets** (dab, jumping, wave, zombie, etc.)

## 🙏 Acknowledgments

**IMPORTANT:** This project is built on top of the excellent work by Facebook Research:

- **Original Project:** [AnimatedDrawings](https://github.com/facebookresearch/AnimatedDrawings)
- **Research Paper:** [A Method for Animating Children's Drawings of the Human Figure](https://dl.acm.org/doi/10.1145/3592788)
- **Authors:** Harrison Jesse Smith, Qingyuan Zheng, Yifei Li, Somya Jain, Jessica K. Hodgins
- **License:** MIT License

We are grateful to the Facebook Research team for making this technology available to the community.

## 🚀 Quick Start

### Prerequisites

- Python 3.8.13 or higher (tested with Python 3.12.4)
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd AnimatedDrawings
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -e .
```

4. **Run the web application:**
```bash
# Testing mode (default)
python app.py

# Production mode
APP_MODE=production python app.py
```

5. **Open your browser:**
```
http://localhost:5001
```

## 🎯 Features

### Testing Mode
- Use pre-loaded sample images from `test_images/` folder
- Quick testing without uploading files
- Perfect for development and demos

### Production Mode
- Upload your own drawings (PNG, JPG up to 16MB)
- Process custom images
- Ready for real-world use

### Animation Options
- **Dab** - Fun dabbing motion
- **Jumping** - Energetic jumping animation
- **Wave Hello** - Friendly waving gesture
- **Zombie** - Spooky zombie walk
- **Jumping Jacks** - Exercise animation

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
