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
    
    %% Styling - Individual Components
    classDef userStyle fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    classDef apiStyle fill:#F5A623,stroke:#C17D11,stroke-width:3px,color:#fff
    classDef serviceStyle fill:#9013FE,stroke:#6B0FC7,stroke-width:2px,color:#fff
    classDef dbStyle fill:#50E3C2,stroke:#3AB89E,stroke-width:2px,color:#000
    classDef configStyle fill:#F8E71C,stroke:#C4B616,stroke-width:2px,color:#000
    classDef engineStyle fill:#E94B3C,stroke:#B83A2E,stroke-width:2px,color:#fff
    classDef fsStyle fill:#7ED321,stroke:#62A519,stroke-width:2px,color:#000
    
    %% Styling - Subgraphs
    classDef servicesGroup fill:#F3E5F5,stroke:#9013FE,stroke-width:3px
    classDef databaseGroup fill:#E0F7FA,stroke:#50E3C2,stroke-width:3px
    classDef configGroup fill:#FFFDE7,stroke:#F8E71C,stroke-width:3px
    classDef animEngineGroup fill:#FFEBEE,stroke:#E94B3C,stroke-width:3px
    classDef fileSystemGroup fill:#F1F8E9,stroke:#7ED321,stroke-width:3px
    
    %% Apply styles to components
    class User userStyle
    class Flask apiStyle
    class ThemeService,ImageService,StorageService serviceStyle
    class ORM,Repo,PG dbStyle
    class ThemeConfig,BVHFiles configStyle
    class Detection,Pose,Rigging,Motion,Render engineStyle
    class Uploads,TestImages,Static,Output fsStyle
    
    %% Apply styles to subgraphs
    class Services servicesGroup
    class Database databaseGroup
    class Config configGroup
    class AnimEngine animEngineGroup
    class FileSystem fileSystemGroup
```

### Color Legend

| Color | Component Type | Description |
|-------|---------------|-------------|
| 🔵 Blue | User Layer | End-user interface (browser) |
| 🟠 Orange | API Layer | Flask web server and REST endpoints |
| 🟣 Purple | Services Layer | Business logic and orchestration |
| 🟢 Cyan | Database Layer | Data persistence and ORM |
| 🟡 Yellow | Configuration | Static configs and motion files |
| 🔴 Red | Animation Engine | Core animation processing pipeline |
| 🟢 Green | File System | File storage and management |

**Connection Types:**
- Solid arrows (→) - Direct data flow and method calls
- Dashed arrows (⋯→) - Configuration loading and reference access

## Data Flow Sequences

### 1. Theme Selection Flow
```mermaid
sequenceDiagram
    participant User
    participant Flask
    participant ThemeService
    participant Repository
    participant Database
    
    User->>Flask: Request theme list
    Flask->>ThemeService: get_all_themes()
    ThemeService->>Repository: find_all()
    Repository->>Database: SELECT * FROM themes
    Database-->>Repository: Theme records
    Repository-->>ThemeService: Theme objects
    ThemeService-->>Flask: List[Theme]
    Flask-->>User: JSON response
```

### 2. Image Upload & Processing Flow
```mermaid
sequenceDiagram
    participant User
    participant Flask
    participant ImageService
    participant StorageService
    participant Repository
    participant Database
    participant FileSystem
    
    User->>Flask: POST /api/upload (image file)
    Flask->>ImageService: validate_image(file)
    ImageService-->>Flask: validation result
    Flask->>StorageService: save_file(file)
    StorageService->>FileSystem: Write to uploads/
    FileSystem-->>StorageService: file path
    StorageService-->>Flask: saved path
    Flask->>Repository: create_drawing(metadata)
    Repository->>Database: INSERT INTO drawings
    Database-->>Repository: drawing_id
    Repository-->>Flask: Drawing object
    Flask-->>User: Success response
```

### 3. Animation Generation Flow
```mermaid
sequenceDiagram
    participant User
    participant Flask
    participant ThemeService
    participant AnimEngine
    participant BVHFiles
    participant FileSystem
    
    User->>Flask: POST /api/animate
    Flask->>ThemeService: get_motion_sequences_for_theme(theme)
    ThemeService-->>Flask: motion list
    Flask->>AnimEngine: start_animation(image, motion)
    AnimEngine->>FileSystem: Load image
    FileSystem-->>AnimEngine: image data
    AnimEngine->>AnimEngine: Character Detection
    AnimEngine->>AnimEngine: Pose Estimation
    AnimEngine->>AnimEngine: Rigging
    AnimEngine->>BVHFiles: Load motion data
    BVHFiles-->>AnimEngine: BVH data
    AnimEngine->>AnimEngine: Motion Retargeting
    AnimEngine->>AnimEngine: Rendering
    AnimEngine->>FileSystem: Save video to output/
    FileSystem-->>AnimEngine: output path
    AnimEngine-->>Flask: video path
    Flask-->>User: Success + video URL
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

### API Layer

**Flask Server (app.py)**
- HTTP request handling
- Route management
- File upload processing
- Mode configuration
- API responses
- Service orchestration

### Services Layer

**ThemeManagerService (services/theme_manager.py)**
- Theme CRUD operations
- Theme validation
- Default theme logic
- Theme-to-motion-sequence mapping
- Theme property retrieval

**ImageProcessingService (services/image_processing_service.py)**
- Image validation (format, size, dimensions)
- Image normalization
- Metadata extraction
- Storage coordination

**StorageService (services/storage_service.py)**
- File system operations
- Upload management
- Test image access
- Output file handling

### Database Layer

**SQLAlchemy ORM (database/orm.py)**
- ORM model definitions
- Session management
- Connection pooling
- Relationship mappings

**Repository Pattern (database/repository.py)**
- Data access abstraction
- CRUD operations
- Query optimization
- Transaction management

**PostgreSQL Database**
- Persistent data storage
- Relational integrity
- Indexed queries
- JSONB for flexible configs

### Configuration Layer

**Theme Configurations (config/themes/*.json)**
- Theme definitions (6 themes)
- Positioning rules
- Motion sequence mappings
- Visual properties

**BVH Motion Files (examples/bvh/)**
- Motion capture data
- Animation sequences
- Character movements

### Animation Engine

**Facebook Animated Drawings**
- Character detection & segmentation
- Pose estimation & joint detection
- Rigging with ARAP deformation
- Motion retargeting from BVH
- Frame rendering & video export

## Layered Architecture

```mermaid
graph TB
    subgraph Presentation["Presentation Layer"]
        UI[Web UI<br/>HTML/CSS/JS]
        API[REST API<br/>Flask Routes]
    end
    
    subgraph Business["Business Logic Layer"]
        ThemeSvc[Theme Manager]
        ImageSvc[Image Processing]
        StorageSvc[Storage Service]
    end
    
    subgraph Data["Data Access Layer"]
        Repo[Repository Pattern]
        ORM[SQLAlchemy ORM]
    end
    
    subgraph Persistence["Persistence Layer"]
        DB[(PostgreSQL)]
        FS[File System]
    end
    
    subgraph External["External Systems"]
        AnimEngine[Animation Engine]
        BVH[BVH Files]
    end
    
    UI --> API
    API --> ThemeSvc
    API --> ImageSvc
    API --> StorageSvc
    
    ThemeSvc --> Repo
    ImageSvc --> Repo
    
    Repo --> ORM
    ORM --> DB
    
    StorageSvc --> FS
    ImageSvc --> FS
    
    API --> AnimEngine
    AnimEngine --> BVH
    AnimEngine --> FS
    
    style Presentation fill:#e1f5ff
    style Business fill:#f3e5f5
    style Data fill:#fff3e0
    style Persistence fill:#e8f5e9
    style External fill:#fce4ec
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

```mermaid
graph LR
    subgraph Frontend["Frontend Stack"]
        HTML[HTML5]
        CSS[CSS3]
        JS[JavaScript ES6+]
        Fetch[Fetch API]
    end
    
    subgraph Backend["Backend Stack"]
        Python[Python 3.8+]
        Flask[Flask 3.1.3]
        SQLAlchemy[SQLAlchemy ORM]
        Psycopg2[psycopg2]
    end
    
    subgraph Database["Database"]
        PostgreSQL[PostgreSQL 12+]
    end
    
    subgraph Animation["Animation Engine"]
        NumPy[NumPy]
        OpenCV[OpenCV]
        Pillow[Pillow]
        PyOpenGL[PyOpenGL]
        GLFW[GLFW]
        SciPy[SciPy]
    end
    
    Frontend --> Backend
    Backend --> Database
    Backend --> Animation
    
    style Frontend fill:#e1f5ff
    style Backend fill:#fff3e0
    style Database fill:#e8f5e9
    style Animation fill:#fce4ec
```

### Stack Details

**Frontend Technologies:**
- HTML5 - Semantic markup
- CSS3 - Gradients, Flexbox, Grid
- Vanilla JavaScript (ES6+) - No framework dependencies
- Fetch API - Async HTTP requests

**Backend Technologies:**
- Python 3.8+ - Core language
- Flask 3.1.3 - Web framework
- SQLAlchemy - ORM and database toolkit
- psycopg2 - PostgreSQL adapter
- Werkzeug - File handling utilities

**Database:**
- PostgreSQL 12+ - Relational database
- JSONB - Flexible configuration storage
- Connection pooling - Performance optimization

**Animation Engine:**
- NumPy - Mathematical operations
- OpenCV - Image processing
- Pillow - Image handling
- PyOpenGL - 3D rendering
- GLFW - Window management
- SciPy - Scientific computing
- Scikit-image - Advanced image processing
- Shapely - Geometric operations

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
