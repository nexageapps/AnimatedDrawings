-- Common Queries for Themed Animation Platform
-- Quick reference for frequently used database operations

-- ============================================================================
-- USER QUERIES
-- ============================================================================

-- Get user by email
SELECT * FROM users WHERE email = 'user@example.com';

-- Get user's total drawings
SELECT email, total_drawings FROM users WHERE email = 'user@example.com';

-- List all users with their drawing counts
SELECT email, total_drawings, created_at 
FROM users 
ORDER BY total_drawings DESC;

-- ============================================================================
-- THEME QUERIES
-- ============================================================================

-- List all available themes
SELECT name, display_name, max_entities FROM themes;

-- Get theme details
SELECT * FROM themes WHERE name = 'jungle';

-- Get theme with positioning rules
SELECT name, display_name, positioning_rules, motion_sequences 
FROM themes 
WHERE name = 'jungle';

-- ============================================================================
-- THEMED WORLD QUERIES
-- ============================================================================

-- Get active (non-full) worlds by theme
SELECT * FROM active_worlds WHERE theme_name = 'jungle';

-- Get world with entity count
SELECT tw.id, t.name as theme, tw.instance_number, tw.entity_count, tw.is_full
FROM themed_worlds tw
JOIN themes t ON tw.theme_id = t.id
WHERE t.name = 'jungle'
ORDER BY tw.instance_number;

-- Find available world for new drawing
SELECT tw.id, tw.entity_count, t.max_entities
FROM themed_worlds tw
JOIN themes t ON tw.theme_id = t.id
WHERE t.name = 'jungle' AND tw.is_full = FALSE
ORDER BY tw.entity_count ASC
LIMIT 1;

-- Get world composition (all entities in a world)
SELECT * FROM world_composition WHERE world_id = 'world-uuid-here';

-- ============================================================================
-- DRAWING QUERIES
-- ============================================================================

-- Get drawing by ID
SELECT * FROM drawing_details WHERE id = 'drawing-uuid-here';

-- Get user's drawings
SELECT id, status, theme_name, created_at, processed_at
FROM drawing_details
WHERE user_email = 'user@example.com'
ORDER BY created_at DESC;

-- Get drawings by status
SELECT id, user_email, status, theme_name, created_at
FROM drawing_details
WHERE status = 'animated'
ORDER BY created_at DESC;

-- Get drawings by theme
SELECT id, user_email, status, created_at
FROM drawing_details
WHERE theme_name = 'jungle'
ORDER BY created_at DESC;

-- Get failed drawings with error messages
SELECT id, user_email, theme_name, error_message, created_at
FROM drawings
WHERE status = 'failed'
ORDER BY created_at DESC;

-- ============================================================================
-- ANIMATION DATA QUERIES
-- ============================================================================

-- Get animation data for a drawing
SELECT ad.*, d.status
FROM animation_data ad
JOIN drawings d ON ad.drawing_id = d.id
WHERE ad.drawing_id = 'drawing-uuid-here';

-- Get successful animations
SELECT d.id, d.user_id, ad.motion_sequence, ad.animation_file_url
FROM animation_data ad
JOIN drawings d ON ad.drawing_id = d.id
WHERE ad.character_detected = TRUE;

-- Get failed character detections
SELECT d.id, d.user_id, d.original_image_url, d.error_message
FROM drawings d
LEFT JOIN animation_data ad ON d.id = ad.drawing_id
WHERE d.status = 'failed' OR ad.character_detected = FALSE;

-- ============================================================================
-- DRAWING ENTITY QUERIES
-- ============================================================================

-- Get entities in a world
SELECT de.*, d.user_id, ad.animation_file_url
FROM drawing_entities de
JOIN drawings d ON de.drawing_id = d.id
LEFT JOIN animation_data ad ON d.id = ad.drawing_id
WHERE de.world_id = 'world-uuid-here'
ORDER BY de.z_index, de.position_y;

-- Check for position collisions (entities within 50 pixels)
SELECT 
    e1.id as entity1_id,
    e2.id as entity2_id,
    SQRT(POWER(e1.position_x - e2.position_x, 2) + POWER(e1.position_y - e2.position_y, 2)) as distance
FROM drawing_entities e1
JOIN drawing_entities e2 ON e1.world_id = e2.world_id AND e1.id < e2.id
WHERE e1.world_id = 'world-uuid-here'
    AND SQRT(POWER(e1.position_x - e2.position_x, 2) + POWER(e1.position_y - e2.position_y, 2)) < 50;

-- Get entity positions in a world
SELECT position_x, position_y, width, height
FROM drawing_entities
WHERE world_id = 'world-uuid-here';

-- ============================================================================
-- PROCESSING JOB QUERIES
-- ============================================================================

-- Get pending jobs
SELECT * FROM processing_jobs 
WHERE status = 'queued' 
ORDER BY priority DESC, created_at ASC;

-- Get job status for a drawing
SELECT job_type, status, attempts, error_message, created_at, completed_at
FROM processing_jobs
WHERE drawing_id = 'drawing-uuid-here'
ORDER BY created_at DESC;

-- Get failed jobs
SELECT pj.*, d.user_id
FROM processing_jobs pj
JOIN drawings d ON pj.drawing_id = d.id
WHERE pj.status = 'failed'
ORDER BY pj.created_at DESC;

-- Get job queue depth by type
SELECT job_type, status, COUNT(*) as count
FROM processing_jobs
GROUP BY job_type, status
ORDER BY job_type, status;

-- Get jobs that need retry
SELECT * FROM processing_jobs
WHERE status = 'failed' AND attempts < max_attempts
ORDER BY created_at ASC;

-- ============================================================================
-- NOTIFICATION QUERIES
-- ============================================================================

-- Get notifications for a user
SELECT notification_type, sent_at, delivery_status
FROM notifications
WHERE user_id = 'user-uuid-here'
ORDER BY sent_at DESC;

-- Get failed notifications
SELECT n.*, u.email
FROM notifications n
JOIN users u ON n.user_id = u.id
WHERE n.delivery_status = 'failed'
ORDER BY n.sent_at DESC;

-- Get notification history for a drawing
SELECT notification_type, sent_at, delivery_status
FROM notifications
WHERE drawing_id = 'drawing-uuid-here'
ORDER BY sent_at DESC;

-- ============================================================================
-- SYSTEM LOG QUERIES
-- ============================================================================

-- Get recent errors
SELECT level, component, message, created_at
FROM system_logs
WHERE level IN ('error', 'critical')
ORDER BY created_at DESC
LIMIT 100;

-- Get logs by component
SELECT level, message, created_at
FROM system_logs
WHERE component = 'animation_engine'
ORDER BY created_at DESC
LIMIT 50;

-- Get error summary by component
SELECT component, level, COUNT(*) as count
FROM system_logs
WHERE level IN ('error', 'critical')
    AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY component, level
ORDER BY count DESC;

-- ============================================================================
-- STATISTICS QUERIES
-- ============================================================================

-- Overall system statistics
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM drawings) as total_drawings,
    (SELECT COUNT(*) FROM drawings WHERE status = 'animated') as animated_drawings,
    (SELECT COUNT(*) FROM drawings WHERE status = 'failed') as failed_drawings,
    (SELECT COUNT(*) FROM themed_worlds) as total_worlds,
    (SELECT COUNT(*) FROM drawing_entities) as total_entities;

-- Drawings by theme
SELECT t.name, t.display_name, COUNT(d.id) as drawing_count
FROM themes t
LEFT JOIN drawings d ON t.id = d.theme_id
GROUP BY t.id, t.name, t.display_name
ORDER BY drawing_count DESC;

-- World occupancy statistics
SELECT 
    t.name as theme,
    COUNT(tw.id) as world_count,
    AVG(tw.entity_count) as avg_entities,
    MAX(tw.entity_count) as max_entities,
    COUNT(CASE WHEN tw.is_full THEN 1 END) as full_worlds
FROM themed_worlds tw
JOIN themes t ON tw.theme_id = t.id
GROUP BY t.name;

-- Processing success rate
SELECT 
    job_type,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*), 2) as success_rate
FROM processing_jobs
GROUP BY job_type;

-- Average processing time by job type
SELECT 
    job_type,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_seconds,
    MIN(EXTRACT(EPOCH FROM (completed_at - started_at))) as min_seconds,
    MAX(EXTRACT(EPOCH FROM (completed_at - started_at))) as max_seconds
FROM processing_jobs
WHERE status = 'completed' AND started_at IS NOT NULL AND completed_at IS NOT NULL
GROUP BY job_type;

-- Most active users
SELECT u.email, u.total_drawings, COUNT(d.id) as verified_count
FROM users u
LEFT JOIN drawings d ON u.id = d.user_id
GROUP BY u.id, u.email, u.total_drawings
ORDER BY u.total_drawings DESC
LIMIT 10;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Find orphaned records (drawings without animation data)
SELECT d.id, d.status, d.created_at
FROM drawings d
LEFT JOIN animation_data ad ON d.id = ad.drawing_id
WHERE d.status = 'animated' AND ad.id IS NULL;

-- Find stale processing jobs (created more than 1 hour ago, still queued)
SELECT * FROM processing_jobs
WHERE status = 'queued' 
    AND created_at < NOW() - INTERVAL '1 hour'
ORDER BY created_at ASC;

-- Clean up old logs (older than 30 days)
-- DELETE FROM system_logs WHERE created_at < NOW() - INTERVAL '30 days';

-- Update world full status based on entity count
UPDATE themed_worlds tw
SET is_full = (tw.entity_count >= t.max_entities)
FROM themes t
WHERE tw.theme_id = t.id;

-- Recalculate user drawing counts
UPDATE users u
SET total_drawings = (
    SELECT COUNT(*) FROM drawings d WHERE d.user_id = u.id
);

-- ============================================================================
-- DEBUGGING QUERIES
-- ============================================================================

-- Check database size
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as database_size;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Check for missing indexes (sequential scans on large tables)
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan as avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;
