-- Rollback Migration: 001_initial_schema.sql
-- Description: Rollback initial database schema for Themed Animation Platform

-- Drop views
DROP VIEW IF EXISTS world_composition;
DROP VIEW IF EXISTS drawing_details;
DROP VIEW IF EXISTS active_worlds;

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_user_drawing_count ON drawings;
DROP TRIGGER IF EXISTS trigger_update_entity_count ON drawing_entities;
DROP TRIGGER IF EXISTS trigger_update_world_timestamp ON drawing_entities;

-- Drop trigger functions
DROP FUNCTION IF EXISTS update_user_drawing_count();
DROP FUNCTION IF EXISTS update_entity_count();
DROP FUNCTION IF EXISTS update_themed_world_timestamp();

-- Drop indexes (will be automatically dropped with tables, but explicit for clarity)
DROP INDEX IF EXISTS idx_system_logs_created_at;
DROP INDEX IF EXISTS idx_system_logs_component;
DROP INDEX IF EXISTS idx_system_logs_level;
DROP INDEX IF EXISTS idx_notifications_sent_at;
DROP INDEX IF EXISTS idx_notifications_drawing_id;
DROP INDEX IF EXISTS idx_notifications_user_id;
DROP INDEX IF EXISTS idx_animation_data_drawing_id;
DROP INDEX IF EXISTS idx_processing_jobs_created_at;
DROP INDEX IF EXISTS idx_processing_jobs_job_type;
DROP INDEX IF EXISTS idx_processing_jobs_drawing_id;
DROP INDEX IF EXISTS idx_processing_jobs_status;
DROP INDEX IF EXISTS idx_themed_worlds_created_at;
DROP INDEX IF EXISTS idx_themed_worlds_is_full;
DROP INDEX IF EXISTS idx_themed_worlds_theme_id;
DROP INDEX IF EXISTS idx_drawing_entities_position;
DROP INDEX IF EXISTS idx_drawing_entities_drawing_id;
DROP INDEX IF EXISTS idx_drawing_entities_world_id;
DROP INDEX IF EXISTS idx_drawings_created_at;
DROP INDEX IF EXISTS idx_drawings_theme_id;
DROP INDEX IF EXISTS idx_drawings_status;
DROP INDEX IF EXISTS idx_drawings_user_id;
DROP INDEX IF EXISTS idx_users_email;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS processing_jobs;
DROP TABLE IF EXISTS drawing_entities;
DROP TABLE IF EXISTS animation_data;
DROP TABLE IF EXISTS drawings;
DROP TABLE IF EXISTS themed_worlds;
DROP TABLE IF EXISTS themes;
DROP TABLE IF EXISTS users;

-- Drop extensions (optional - may be used by other databases)
-- DROP EXTENSION IF EXISTS "pgcrypto";
