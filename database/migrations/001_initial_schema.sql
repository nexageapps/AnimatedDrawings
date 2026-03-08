-- Migration: 001_initial_schema.sql
-- Description: Initial database schema for Themed Animation Platform
-- Created: 2024
-- Requirements: 2.2, 2.3, 9.1, 9.2

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Stores user information based on email identification
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_drawings INTEGER DEFAULT 0,
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ============================================================================
-- THEMES TABLE
-- ============================================================================
-- Stores theme definitions and properties
CREATE TABLE themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    background_image_url TEXT,
    dimensions_width INTEGER NOT NULL,
    dimensions_height INTEGER NOT NULL,
    max_entities INTEGER DEFAULT 50,
    positioning_rules JSONB,
    motion_sequences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT positive_dimensions CHECK (dimensions_width > 0 AND dimensions_height > 0),
    CONSTRAINT positive_max_entities CHECK (max_entities > 0)
);

-- ============================================================================
-- THEMED WORLDS TABLE
-- ============================================================================
-- Stores themed world instances
CREATE TABLE themed_worlds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    theme_id UUID NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    instance_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entity_count INTEGER DEFAULT 0,
    is_full BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_theme_instance UNIQUE(theme_id, instance_number),
    CONSTRAINT non_negative_entity_count CHECK (entity_count >= 0),
    CONSTRAINT positive_instance_number CHECK (instance_number > 0)
);

-- ============================================================================
-- DRAWINGS TABLE
-- ============================================================================
-- Stores drawing metadata and processing status
CREATE TABLE drawings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_image_url TEXT NOT NULL,
    normalized_image_url TEXT,
    status VARCHAR(50) NOT NULL,
    theme_id UUID REFERENCES themes(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    error_message TEXT,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'processing', 'animated', 'failed'))
);

-- ============================================================================
-- ANIMATION DATA TABLE
-- ============================================================================
-- Stores animation processing results
CREATE TABLE animation_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID UNIQUE NOT NULL REFERENCES drawings(id) ON DELETE CASCADE,
    character_detected BOOLEAN NOT NULL,
    segmentation_mask_url TEXT,
    skeleton_data JSONB,
    motion_sequence VARCHAR(100),
    animation_file_url TEXT,
    sprite_sheet_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DRAWING ENTITIES TABLE
-- ============================================================================
-- Stores drawing placements in themed worlds
CREATE TABLE drawing_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id) ON DELETE CASCADE,
    world_id UUID NOT NULL REFERENCES themed_worlds(id) ON DELETE CASCADE,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    z_index INTEGER DEFAULT 0,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_drawing_in_world UNIQUE(drawing_id, world_id),
    CONSTRAINT positive_dimensions CHECK (width > 0 AND height > 0),
    CONSTRAINT non_negative_position CHECK (position_x >= 0 AND position_y >= 0)
);

-- ============================================================================
-- PROCESSING JOBS TABLE
-- ============================================================================
-- Stores background job queue and status
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT valid_job_type CHECK (job_type IN ('image_processing', 'animation', 'composition')),
    CONSTRAINT valid_job_status CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    CONSTRAINT non_negative_attempts CHECK (attempts >= 0),
    CONSTRAINT positive_max_attempts CHECK (max_attempts > 0)
);

-- ============================================================================
-- NOTIFICATIONS TABLE
-- ============================================================================
-- Stores notification history
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    drawing_id UUID REFERENCES drawings(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_content TEXT,
    delivery_status VARCHAR(50) DEFAULT 'sent',
    CONSTRAINT valid_notification_type CHECK (notification_type IN ('success', 'error', 'acknowledgment')),
    CONSTRAINT valid_delivery_status CHECK (delivery_status IN ('sent', 'failed', 'pending'))
);

-- ============================================================================
-- SYSTEM LOGS TABLE
-- ============================================================================
-- Stores system-wide logs for monitoring and debugging
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_log_level CHECK (level IN ('info', 'warning', 'error', 'critical'))
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);

-- Drawings indexes
CREATE INDEX idx_drawings_user_id ON drawings(user_id);
CREATE INDEX idx_drawings_status ON drawings(status);
CREATE INDEX idx_drawings_theme_id ON drawings(theme_id);
CREATE INDEX idx_drawings_created_at ON drawings(created_at);

-- Drawing entities indexes
CREATE INDEX idx_drawing_entities_world_id ON drawing_entities(world_id);
CREATE INDEX idx_drawing_entities_drawing_id ON drawing_entities(drawing_id);
CREATE INDEX idx_drawing_entities_position ON drawing_entities(position_x, position_y);

-- Themed worlds indexes
CREATE INDEX idx_themed_worlds_theme_id ON themed_worlds(theme_id);
CREATE INDEX idx_themed_worlds_is_full ON themed_worlds(is_full);
CREATE INDEX idx_themed_worlds_created_at ON themed_worlds(created_at);

-- Processing jobs indexes
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX idx_processing_jobs_drawing_id ON processing_jobs(drawing_id);
CREATE INDEX idx_processing_jobs_job_type ON processing_jobs(job_type);
CREATE INDEX idx_processing_jobs_created_at ON processing_jobs(created_at);

-- Animation data indexes
CREATE INDEX idx_animation_data_drawing_id ON animation_data(drawing_id);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_drawing_id ON notifications(drawing_id);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at);

-- System logs indexes
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_component ON system_logs(component);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update last_updated timestamp on themed_worlds when entity_count changes
CREATE OR REPLACE FUNCTION update_themed_world_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE themed_worlds 
    SET last_updated = CURRENT_TIMESTAMP 
    WHERE id = NEW.world_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_world_timestamp
AFTER INSERT OR UPDATE ON drawing_entities
FOR EACH ROW
EXECUTE FUNCTION update_themed_world_timestamp();

-- Update entity_count on themed_worlds when drawing_entities are added/removed
CREATE OR REPLACE FUNCTION update_entity_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE themed_worlds 
        SET entity_count = entity_count + 1 
        WHERE id = NEW.world_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE themed_worlds 
        SET entity_count = entity_count - 1 
        WHERE id = OLD.world_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_entity_count
AFTER INSERT OR DELETE ON drawing_entities
FOR EACH ROW
EXECUTE FUNCTION update_entity_count();

-- Update total_drawings count on users when drawings are added/removed
CREATE OR REPLACE FUNCTION update_user_drawing_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE users 
        SET total_drawings = total_drawings + 1 
        WHERE id = NEW.user_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE users 
        SET total_drawings = total_drawings - 1 
        WHERE id = OLD.user_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_drawing_count
AFTER INSERT OR DELETE ON drawings
FOR EACH ROW
EXECUTE FUNCTION update_user_drawing_count();

-- ============================================================================
-- INITIAL DATA - DEFAULT THEMES
-- ============================================================================

INSERT INTO themes (name, display_name, dimensions_width, dimensions_height, max_entities, positioning_rules, motion_sequences) VALUES
('jungle', 'Jungle Adventure', 1920, 1080, 50, 
 '{"type": "ground_based", "vertical_layering": true, "ground_y": 900}',
 '["walk", "run", "climb", "swing"]'),
 
('christmas', 'Christmas Wonderland', 1920, 1080, 50,
 '{"type": "clustered", "center_point": [960, 540], "allow_floating": true}',
 '["dance", "wave", "celebrate", "gift_giving"]'),
 
('party', 'Party Time', 1920, 1080, 50,
 '{"type": "random", "allow_elevated": true}',
 '["dance", "jump", "celebrate", "cheer"]'),
 
('school', 'School Days', 1920, 1080, 50,
 '{"type": "row_based", "rows": 5, "structured": true}',
 '["walk", "sit", "raise_hand", "read"]'),
 
('ocean', 'Ocean World', 1920, 1080, 50,
 '{"type": "depth_layers", "layers": 3, "floating": true}',
 '["swim", "float", "dive", "wave"]'),
 
('general', 'General', 1920, 1080, 50,
 '{"type": "grid", "balanced": true}',
 '["idle", "walk", "wave"]');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for active worlds (not full)
CREATE VIEW active_worlds AS
SELECT 
    tw.id,
    tw.theme_id,
    t.name as theme_name,
    t.display_name as theme_display_name,
    tw.instance_number,
    tw.entity_count,
    tw.created_at,
    tw.last_updated
FROM themed_worlds tw
JOIN themes t ON tw.theme_id = t.id
WHERE tw.is_full = FALSE;

-- View for drawing details with animation status
CREATE VIEW drawing_details AS
SELECT 
    d.id,
    d.user_id,
    u.email as user_email,
    d.original_image_url,
    d.normalized_image_url,
    d.status,
    d.theme_id,
    t.name as theme_name,
    d.created_at,
    d.processed_at,
    ad.character_detected,
    ad.animation_file_url,
    de.world_id,
    de.position_x,
    de.position_y
FROM drawings d
JOIN users u ON d.user_id = u.id
LEFT JOIN themes t ON d.theme_id = t.id
LEFT JOIN animation_data ad ON d.id = ad.drawing_id
LEFT JOIN drawing_entities de ON d.id = de.drawing_id;

-- View for world composition (all entities in a world)
CREATE VIEW world_composition AS
SELECT 
    tw.id as world_id,
    t.name as theme_name,
    t.display_name as theme_display_name,
    t.background_image_url,
    tw.entity_count,
    de.id as entity_id,
    de.drawing_id,
    de.position_x,
    de.position_y,
    de.z_index,
    de.width,
    de.height,
    ad.animation_file_url,
    u.email as owner_email
FROM themed_worlds tw
JOIN themes t ON tw.theme_id = t.id
LEFT JOIN drawing_entities de ON tw.id = de.world_id
LEFT JOIN drawings d ON de.drawing_id = d.id
LEFT JOIN animation_data ad ON d.id = ad.drawing_id
LEFT JOIN users u ON d.user_id = u.id;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'Stores user information identified by email address';
COMMENT ON TABLE themes IS 'Stores theme definitions with positioning rules and visual properties';
COMMENT ON TABLE themed_worlds IS 'Stores instances of themed worlds that contain drawing entities';
COMMENT ON TABLE drawings IS 'Stores drawing metadata and processing status';
COMMENT ON TABLE animation_data IS 'Stores animation processing results from Facebook Animated Drawings';
COMMENT ON TABLE drawing_entities IS 'Stores drawing placements within themed worlds';
COMMENT ON TABLE processing_jobs IS 'Stores background job queue for asynchronous processing';
COMMENT ON TABLE notifications IS 'Stores notification history sent to users';
COMMENT ON TABLE system_logs IS 'Stores system-wide logs for monitoring and debugging';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
