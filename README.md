<div align="center">

# DrawWorld

**Transform drawings into animated characters in shared themed worlds**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sponsored by NexageApps](https://img.shields.io/badge/Sponsored%20by-NexageApps-orange.svg)](https://nexageapps.com)

A multi-user platform built on [Facebook Research's AnimatedDrawings](https://github.com/facebookresearch/AnimatedDrawings)

[Features](#key-features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Overview

DrawWorld accepts drawing images, automatically animates them using AI-powered character detection, and places them into collaborative themed environments where multiple users' creations coexist and interact spatially.

---

## Key Features
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development Status](#development-status)
- [Technology Stack](#technology-stack)
- [Technical Details](#technical-details)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Resources](#resources)
- [Citation](#citation)

---

- **Email-based submission workflow** - Send drawings via email with theme specifications
- **AI-powered animation** - Automatic character detection and animation using Facebook's Animated Drawings
- **Themed virtual worlds** - Shared environments (jungle, christmas, party, school, ocean) where drawings come together
- **Intelligent spatial positioning** - Smart placement with collision avoidance and theme-aware rules
- **Multi-user collaboration** - Multiple users' drawings coexist in the same themed world
- **Dual operation modes** - Testing mode for development, production mode for email-based workflow

## Technology Stack

- **Backend:** Python 3.8+, Flask, SQLAlchemy
- **Database:** PostgreSQL 12+
- **Cache & Queue:** Redis, Celery
- **Animation:** Facebook Animated Drawings (PyTorch)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Rendering:** FFmpeg, Three.js (planned)

## Acknowledgments

This project is built on top of the excellent work by Facebook Research:

- **Original Project:** [AnimatedDrawings](https://github.com/facebookresearch/AnimatedDrawings)
- **Research Paper:** [A Method for Animating Children's Drawings of the Human Figure](https://dl.acm.org/doi/10.1145/3592788)
- **Authors:** Harrison Jesse Smith, Qingyuan Zheng, Yifei Li, Somya Jain, Jessica K. Hodgins
- **License:** MIT License

We are grateful to the Facebook Research team for making this technology available to the community.

## Sponsorship

This project is sponsored by [NexageApps](https://nexageapps.com) - Building innovative digital solutions.

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

## Project Structure

```
AnimatedDrawings/
├── app.py                          # Flask web application
├── database/                       # Database layer
│   ├── connection.py              # Database connection management
│   ├── orm.py                     # SQLAlchemy ORM models
│   ├── repository.py              # Data access layer
│   ├── migrate.py                 # Migration runner
│   └── migrations/                # SQL migration files
├── models/                         # Domain models
│   ├── drawing.py                 # Drawing entity model
│   ├── theme.py                   # Theme model
│   ├── drawing_entity.py          # Placed drawing in world
│   └── processing_job.py          # Background job model
├── services/                       # Business logic services (to be implemented)
│   ├── email_receiver.py          # Email monitoring and parsing
│   ├── image_processor.py         # Image validation and storage
│   ├── animation_engine.py        # Animation generation
│   ├── world_compositor.py        # Spatial positioning
│   ├── rendering.py               # Scene rendering
│   └── notification.py            # Email notifications
├── templates/                      # HTML templates
│   └── index.html                 # Main UI
├── static/                         # Static assets
│   ├── css/style.css              # Styling
│   └── js/app.js                  # Frontend logic
├── animated_drawings/              # Core animation library (Facebook Research)
├── examples/                       # Example configurations and BVH files
├── test_images/                    # Sample images for testing mode
├── uploads/                        # User uploaded images
├── .kiro/specs/                    # Project specifications
│   └── themed-animation-platform/
│       ├── requirements.md        # Detailed requirements
│       ├── design.md              # Architecture and design
│       └── tasks.md               # Implementation plan
└── README.md                       # This file
```

## Testing

### Testing Mode

Testing mode allows rapid development without email infrastructure:

1. Start the application in testing mode:
```bash
./run_testing.sh
```

2. Access the web UI at `http://localhost:5001`

3. Upload drawings directly or select from test images

4. Choose a theme and generate animation

5. View the animated drawing in the themed world

### Add Test Images

Place test images in the `test_images/` folder:

```bash
cp your_drawing.png test_images/
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_models.py
pytest database/test_schema.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Application Mode
APP_MODE=testing  # or 'production'
PORT=5001

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/themed_animations

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Production Mode)
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-app-password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# Storage Configuration
STORAGE_TYPE=local  # or 's3'
STORAGE_PATH=./uploads
# S3_BUCKET=your-bucket-name
# S3_REGION=us-east-1

# Processing Configuration
MAX_IMAGE_SIZE_MB=10
MAX_ENTITIES_PER_WORLD=50
MIN_ENTITY_SPACING_PX=50
ANIMATION_TIMEOUT_SECONDS=300

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Theme Configuration

Themes are defined in the database and can be customized. Each theme includes:

- Display name and identifier
- Background image URL
- World dimensions (width x height)
- Positioning rules (ground-based, floating, clustered, etc.)
- Motion sequence mappings
- Maximum entity capacity

## Technical Details

### Animation Pipeline

1. **Character Detection** - AI detects human figure in drawing using Facebook Animated Drawings
2. **Segmentation** - Generates mask separating character from background
3. **Joint Annotation** - Identifies joint locations (head, torso, arms, legs)
4. **Skeleton Rigging** - Creates skeletal structure for animation
5. **Motion Retargeting** - Applies BVH motion data with theme-aware selection
6. **Export** - Generates animation data for rendering

### Spatial Positioning Algorithm

The World Compositor uses an intelligent grid-based algorithm:

1. Analyze entity visual characteristics (size, orientation)
2. Apply theme-specific positioning rules
3. Find available space with minimum 50px spacing
4. Calculate position score based on distribution balance
5. Assign optimal coordinates with collision avoidance

### Database Schema

Core tables:
- `users` - Email-based user identification
- `themes` - Theme definitions and properties
- `themed_worlds` - World instances for each theme
- `drawings` - User-submitted drawings and processing status
- `animation_data` - Generated animation artifacts
- `drawing_entities` - Placed drawings in worlds with coordinates
- `processing_jobs` - Background job queue and status
- `notifications` - Email notification tracking

See `database/migrations/001_initial_schema.sql` for complete schema.

## Original Documentation

For detailed information about the underlying AnimatedDrawings technology:

- **[README_ORIGINAL.md](README_ORIGINAL.md)** - Complete original documentation
- **[examples/config/README.md](examples/config/README.md)** - Configuration file documentation
- **[.kiro/specs/themed-animation-platform/](/.kiro/specs/themed-animation-platform/)** - Project specifications

## Development Status

This is an active development project following the implementation plan in `.kiro/specs/themed-animation-platform/tasks.md`.

### Completed

- Database schema and migrations
- Core domain models (Drawing, Theme, DrawingEntity, ProcessingJob)
- ORM layer with SQLAlchemy
- Repository pattern for data access
- Basic web UI with mode switching
- Testing mode infrastructure

### In Progress

- Theme management system
- Image processing service
- Animation engine integration
- World compositor service
- Email receiver service
- Background job processing with Celery
- Rendering service
- Notification service

### Planned

- REST API endpoints
- Frontend enhancements for world viewing
- Performance optimization
- Comprehensive testing suite
- Docker deployment configuration
- Production deployment

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** and create your branch from `main`
2. **Review specifications** in `.kiro/specs/themed-animation-platform/`
3. **Follow the implementation plan** in `tasks.md`
4. **Write tests** for new features (pytest + Hypothesis)
5. **Update documentation** as needed
6. **Test thoroughly** in both Testing and Production modes
7. **Submit a pull request** with a clear description

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write meaningful commit messages
- Add docstrings to all functions and classes
- Ensure all tests pass before submitting PR
- Acknowledge the original Facebook Research project in relevant code

### Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## API Documentation

### REST Endpoints

```
GET  /api/v1/worlds/{world_id}           - View themed world with all entities
GET  /api/v1/worlds?theme={theme}        - List worlds by theme (paginated)
GET  /api/v1/drawings/{drawing_id}       - Get drawing details and status
GET  /api/v1/users/{email}/drawings      - List user's drawings
GET  /api/v1/health                      - System health check
```

See design document for complete API specification.

## Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

1. Set up PostgreSQL and Redis
2. Configure environment variables
3. Run database migrations
4. Start Celery workers
5. Start Flask application
6. Configure reverse proxy (nginx)

See `DEPLOYMENT_READY.md` for detailed deployment instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This maintains compatibility with the original AnimatedDrawings project license.

### Third-Party Licenses

- **AnimatedDrawings:** MIT License - Facebook Research
- **Flask:** BSD-3-Clause License
- **SQLAlchemy:** MIT License
- **Celery:** BSD License

## Resources

### Project Links
- **Documentation:** [.kiro/specs/themed-animation-platform/](.kiro/specs/themed-animation-platform/)
- **Issue Tracker:** [GitHub Issues](../../issues)
- **Sponsor:** [NexageApps](https://nexageapps.com)

### Original AnimatedDrawings
- **Repository:** https://github.com/facebookresearch/AnimatedDrawings
- **Research Paper:** https://dl.acm.org/doi/10.1145/3592788
- **Demo Website:** https://sketch.metademolab.com/

## Support

For issues related to:
- **DrawWorld Platform:** Open an issue in this repository
- **Core Animation Library:** Refer to the [original project](https://github.com/facebookresearch/AnimatedDrawings)
- **Commercial Support:** Contact [NexageApps](https://nexageapps.com)

## Citation

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

<div align="center">

**DrawWorld** - Sponsored by [NexageApps](https://nexageapps.com)

Built on top of Facebook Research's AnimatedDrawings

[⬆ Back to Top](#drawworld)

</div>
