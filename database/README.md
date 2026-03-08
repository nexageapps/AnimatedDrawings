# Database Schema and Migrations

This directory contains the PostgreSQL database schema and migration scripts for the Themed Animation Platform.

## Overview

The database schema supports:
- User management (email-based identification)
- Theme definitions and properties
- Themed world instances
- Drawing storage and processing status
- Animation data from Facebook Animated Drawings
- Spatial positioning of drawings in worlds
- Background job processing queue
- Notification tracking
- System logging

## Requirements

- PostgreSQL 12 or higher
- Python 3.8+ (for migration script)
- psycopg2 library

## Installation

1. Install PostgreSQL:
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

2. Install Python dependencies:
```bash
pip install psycopg2-binary
```

3. Create database:
```bash
createdb themed_animation
```

## Usage

### Apply Migrations

Apply all pending migrations:
```bash
python database/migrate.py migrate
```

With custom connection string:
```bash
python database/migrate.py migrate --connection-string "postgresql://user:password@localhost/themed_animation"
```

Using environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost/themed_animation"
python database/migrate.py migrate
```

Dry run (see what would be applied):
```bash
python database/migrate.py migrate --dry-run
```

### Check Migration Status

```bash
python database/migrate.py status
```

### Rollback Migration

```bash
python database/migrate.py rollback --migration 001_initial_schema
```

## Database Schema

### Tables

1. **users** - User accounts identified by email
2. **themes** - Theme definitions (jungle, christmas, party, school, ocean, general)
3. **themed_worlds** - Instances of themed worlds
4. **drawings** - Drawing metadata and processing status
5. **animation_data** - Animation processing results
6. **drawing_entities** - Drawing placements in worlds
7. **processing_jobs** - Background job queue
8. **notifications** - Notification history
9. **system_logs** - System-wide logs

### Views

1. **active_worlds** - Non-full worlds available for new drawings
2. **drawing_details** - Complete drawing information with joins
3. **world_composition** - All entities in a world with metadata

### Indexes

Performance indexes are created on:
- Foreign key columns
- Status and type columns
- Timestamp columns for time-based queries
- Position columns for spatial queries

### Triggers

1. **update_themed_world_timestamp** - Updates last_updated on entity changes
2. **update_entity_count** - Maintains entity_count on themed_worlds
3. **update_user_drawing_count** - Maintains total_drawings on users

## Connection String Format

```
postgresql://[user[:password]@][host][:port][/database]
```

Examples:
```
postgresql://localhost/themed_animation
postgresql://user:pass@localhost:5432/themed_animation
postgresql://user:pass@db.example.com/themed_animation
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://localhost/themed_animation`)

## Migration Files

Migrations are located in `database/migrations/` and follow the naming convention:
- `NNN_description.sql` - Forward migration
- `NNN_description_rollback.sql` - Rollback migration

Current migrations:
- `001_initial_schema.sql` - Initial database schema with all tables

## Default Data

The initial migration includes default theme data:
- jungle (Jungle Adventure)
- christmas (Christmas Wonderland)
- party (Party Time)
- school (School Days)
- ocean (Ocean World)
- general (General)

## Testing

For testing, you can create a separate test database:

```bash
createdb themed_animation_test
export DATABASE_URL="postgresql://localhost/themed_animation_test"
python database/migrate.py migrate
```

## Backup and Restore

### Backup
```bash
pg_dump themed_animation > backup.sql
```

### Restore
```bash
psql themed_animation < backup.sql
```

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Check PostgreSQL is running: `pg_isready`
2. Verify database exists: `psql -l`
3. Check connection string format
4. Verify user permissions

### Migration Errors

If a migration fails:
1. Check the error message in the output
2. Verify PostgreSQL version compatibility
3. Check for existing tables/conflicts
4. Review migration SQL for syntax errors
5. Use rollback if needed

### Reset Database

To completely reset the database:
```bash
dropdb themed_animation
createdb themed_animation
python database/migrate.py migrate
```

## Performance Considerations

The schema includes:
- Indexes on frequently queried columns
- JSONB for flexible theme configuration
- Triggers for automatic counter updates
- Views for common query patterns
- Constraints for data integrity

## Security

- Use strong passwords for database users
- Limit database user permissions
- Use SSL for remote connections
- Regularly backup data
- Monitor system_logs for suspicious activity

## Requirements Mapping

This schema satisfies the following requirements:
- **Requirement 2.2**: Unique identifier assignment for stored images
- **Requirement 2.3**: Email address association with stored images
- **Requirement 9.1**: Drawing entity metadata storage
- **Requirement 9.2**: Themed world and entity relationship persistence
