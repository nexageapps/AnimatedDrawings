# 🏗️ Architecture Overview

## System Architecture Diagram

```mermaid
graph TB
    %% User Layer
    User[👤 User Browser<br/>http://localhost:5001]
    
    %% API Layer
    Flask[🌐 Flask Web Server<br/>app.py]
    
    %% Service Layer
    subgraph Services["🔧 Services Layer"]
        ThemeService[ThemeManagerService<br/>Theme CRUD & Validation]
        ImageService[ImageProcessingService<br/>Image Validation & Storage]
        StorageService[StorageService<br/>File Management]
    end
    
    %% Database Layer
    subgraph Database["💾 Database Layer"]
        ORM[SQLAlchemy ORM<br/>Models & Sessions]
        Repo[Repository Pattern<br/>Data Access]
        PG[(PostgreSQL<br/>themed_animation)]
    end
    
    %% Configuration
    subgraph Config["⚙️ Configuration"]
        ThemeConfig[Theme Configs<br/>config/themes/*.json]
        BVHFiles[BVH Motion Files<br/>examples/bvh/]
    end
    
    %% Animation Engine
    subgraph AnimEngine["🎬 Animation Engine"]
        Detection[Character Detection<br/>Segmentation]
        Pose[Pose Estimation<br/>Joint Detection]
        Rigging[Rigging<br/>ARAP Deformation]
        Motion[Motion Retargeting<br/>BVH Application]
        Render[Rendering<br/>GIF/MP4 Export]
    end
    
    %% File Storage
    subgraph FileSystem["📁 File System"]
        Uploads[uploads/<br/>User Images]
        TestImages[test_images/<br/>Test Data]
        Static[static/<br/>CSS, JS, Backgrounds]
        Output[output/<br/>Generated Videos]
    end
    
    %% Connections - User to API
    User -->|HTTP Requests| Flask
    Flask -->|HTML Response| User
    
    %% Connections - API to Services
    Flask -->|Get/Validate Theme| ThemeService
    Flask -->|Process Image| ImageService
    Flask -->|Store/Retrieve Files| StorageService
    
    %% Connections - Services to Database
    ThemeService -->|Query Themes| Repo
    ImageService -->|Store Metadata| Repo
    Repo -->|ORM Operations| ORM
    ORM -->|SQL Queries| PG
    
    %% Connections - Services to Config
    ThemeService -.->|Load Configs| ThemeConfig
    ThemeService -.->|Get Motions| BVHFiles
    
    %% Connections - Services to File System
    ImageService -->|Save/Load| Uploads
    StorageService -->|Manage Files| Uploads
    StorageService -->|Access Test Data| TestImages
    Flask -.->|Serve Static| Static
    
    %% Connections - Animation Pipeline
    Flask -->|Trigger Animation| Detection
    Detection -->|Character Data| Pose
    Pose -->|Skeleton| Rigging
    Rigging -->|Rigged Character| Motion
    Motion -->|Apply BVH| Render
    Render -->|Save Video| Output
    Output -->|Return Path| Flask
    
    %% Motion files to Animation
    BVHFiles -.->|Motion Data| Motion
    
    %% Styling
    classDef userStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef apiStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef serviceStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dbStyle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef configStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef engineStyle fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef fsStyle fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    
    class User userStyle
    class Flask apiStyle
    class ThemeService,ImageService,StorageService serviceStyle
    class ORM,Repo,PG dbStyle
    class ThemeConfig,BVHFiles configStyle
    class Detection,Pose,Rigging,Motion,Render engineStyle
    class Uploads,TestImages,Static,Output fsStyle
```

## Component Breakdown

### Frontend Layer

**HTML (templates/index.html)**
- Main UI structure
- Mode toggle buttons
- Image display areas
- Upload interface
- Animation controls

**CSS (static/css/style.css)**
- Visual styling
- Responsive layout
- Animations & transitions
- Color scheme

**JavaScript (static/js/app.js)**
- User interactions
- API communication
- Dynamic UI updates
- File handling

### Backend Layer

**Flask Server (app.py)**
- HTTP request handling
- Route management
- File upload processing
- Mode configuration
- API responses

### Data Flow

```
User Action → Frontend JS → API Request → Flask Server
                                              ↓
                                         File System
                                              ↓
                                    Animation Engine
                                              ↓
                                         Output File
                                              ↓
                                    Response to User
```

## Mode Architecture

### Testing Mode
```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
         │ Select test image
         │
┌────────▼────────┐
│  test_images/   │
│  • garlic.png   │
└────────┬────────┘
         │
         │ Process
         │
┌────────▼────────┐
│ Animation Core  │
└────────┬────────┘
         │
         │ Output
         │
┌────────▼────────┐
│   video.gif     │
└─────────────────┘
```

### Production Mode
```
┌─────────────────┐
│  User Browser   │
└────────┬────────┘
         │
         │ Upload image
         │
┌────────▼────────┐
│   uploads/      │
│  • user1.png    │
└────────┬────────┘
         │
         │ Process
         │
┌────────▼────────┐
│ Animation Core  │
└────────┬────────┘
         │
         │ Output
         │
┌────────▼────────┐
│   video.gif     │
└─────────────────┘
```

## API Endpoints

### GET /
Returns the main HTML page

### GET /api/mode
```json
Response: {
  "mode": "testing" | "production"
}
```

### GET /api/test-images
```json
Response: {
  "images": [
    {
      "name": "garlic.png",
      "path": "test_images/garlic.png"
    }
  ]
}
```

### POST /api/upload
```
Request: multipart/form-data with file
Response: {
  "success": true,
  "filename": "image.png",
  "message": "File uploaded successfully"
}
```

### POST /api/animate
```json
Request: {
  "image_path": "test_images/garlic.png",
  "motion": "dab"
}

Response: {
  "success": true,
  "message": "Animation started",
  "output": "video.gif"
}
```

## Technology Stack

```
┌─────────────────────────────────────┐
│          Frontend Stack              │
├─────────────────────────────────────┤
│ • HTML5                              │
│ • CSS3 (Gradients, Flexbox, Grid)   │
│ • Vanilla JavaScript (ES6+)         │
│ • Fetch API                          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│          Backend Stack               │
├─────────────────────────────────────┤
│ • Python 3.8+                        │
│ • Flask 3.1.3                        │
│ • Werkzeug (File handling)           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        Animation Engine              │
├─────────────────────────────────────┤
│ • NumPy (Math operations)            │
│ • OpenCV (Image processing)          │
│ • Pillow (Image handling)            │
│ • PyOpenGL (Rendering)               │
│ • GLFW (Window management)           │
│ • SciPy (Scientific computing)       │
│ • Scikit-image (Image processing)    │
│ • Shapely (Geometry)                 │
└─────────────────────────────────────┘
```

## Security Considerations

1. **File Upload Validation**
   - File type checking
   - Size limits (16MB)
   - Secure filename handling

2. **Path Security**
   - No directory traversal
   - Sandboxed upload folder
   - Validated file paths

3. **Input Sanitization**
   - JSON validation
   - Parameter checking
   - Error handling

## Performance Considerations

1. **File Handling**
   - Streaming uploads
   - Temporary storage
   - Cleanup routines

2. **Animation Processing**
   - Background processing (future)
   - Progress tracking (future)
   - Queue management (future)

3. **Caching**
   - Static file caching
   - Result caching (future)

## Scalability Path

### Current (Single User)
```
User → Flask Dev Server → Local Processing
```

### Future (Multi User)
```
Users → Load Balancer → Flask Servers → Task Queue → Workers
                                              ↓
                                         Database
                                              ↓
                                      File Storage
```

## Deployment Options

### Development
```bash
python app.py
# Flask development server
# Debug mode enabled
# Auto-reload on changes
```

### Production (Future)
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
# Multiple workers
# Production WSGI server
# Better performance
```

## Monitoring Points

1. **Server Health**
   - Uptime
   - Response times
   - Error rates

2. **File System**
   - Upload folder size
   - Disk space
   - File cleanup

3. **Processing**
   - Animation queue length
   - Processing times
   - Success/failure rates

---

**Architecture Version:** 1.0
**Last Updated:** March 2026
