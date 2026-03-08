"""
Database Theme Seeding Script

Seeds the database with initial theme configurations from JSON files.

Requirements: 4.1, 4.5
"""

import json
import logging
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.orm import init_db, get_session, Theme as ThemeORM, create_all_tables
from models.theme import Theme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_theme_config(config_path: Path) -> dict:
    """Load theme configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def create_theme_from_config(config: dict) -> Theme:
    """Create Theme domain model from configuration dictionary"""
    return Theme(
        id=str(uuid4()),
        name=config['name'],
        display_name=config['display_name'],
        background_image_url=config['background_image_url'],
        dimensions=(config['dimensions']['width'], config['dimensions']['height']),
        max_entities=config['max_entities'],
        positioning_rules=config['positioning_rules'],
        motion_sequences=config['motion_sequences']
    )


def seed_themes(config_dir: Path = None):
    """
    Seed database with theme configurations.
    
    Args:
        config_dir: Path to directory containing theme JSON files
    """
    if config_dir is None:
        config_dir = Path(__file__).parent.parent / 'config' / 'themes'
    
    if not config_dir.exists():
        logger.error(f"Theme config directory not found: {config_dir}")
        return False
    
    # Get all JSON files in config directory
    config_files = list(config_dir.glob('*.json'))
    if not config_files:
        logger.warning(f"No theme configuration files found in {config_dir}")
        return False
    
    logger.info(f"Found {len(config_files)} theme configuration files")
    
    session = get_session()
    try:
        themes_created = 0
        themes_updated = 0
        
        for config_file in config_files:
            try:
                # Load configuration
                config = load_theme_config(config_file)
                theme_name = config['name']
                
                logger.info(f"Processing theme: {theme_name}")
                
                # Check if theme already exists
                existing_theme = session.query(ThemeORM).filter_by(name=theme_name).first()
                
                if existing_theme:
                    # Update existing theme
                    logger.info(f"Theme '{theme_name}' already exists, updating...")
                    existing_theme.display_name = config['display_name']
                    existing_theme.background_image_url = config['background_image_url']
                    existing_theme.dimensions_width = config['dimensions']['width']
                    existing_theme.dimensions_height = config['dimensions']['height']
                    existing_theme.max_entities = config['max_entities']
                    existing_theme.positioning_rules = config['positioning_rules']
                    existing_theme.motion_sequences = config['motion_sequences']
                    themes_updated += 1
                else:
                    # Create new theme
                    theme = create_theme_from_config(config)
                    theme_orm = ThemeORM(
                        id=theme.id,
                        name=theme.name,
                        display_name=theme.display_name,
                        background_image_url=theme.background_image_url,
                        dimensions_width=theme.dimensions[0],
                        dimensions_height=theme.dimensions[1],
                        max_entities=theme.max_entities,
                        positioning_rules=theme.positioning_rules,
                        motion_sequences=theme.motion_sequences
                    )
                    session.add(theme_orm)
                    themes_created += 1
                    logger.info(f"Created theme: {theme_name}")
                
            except Exception as e:
                logger.error(f"Error processing {config_file.name}: {e}")
                continue
        
        # Commit all changes
        session.commit()
        
        logger.info(f"Theme seeding complete: {themes_created} created, {themes_updated} updated")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding themes: {e}")
        return False
    finally:
        session.close()


def verify_themes():
    """Verify that all themes were seeded correctly"""
    session = get_session()
    try:
        themes = session.query(ThemeORM).all()
        logger.info(f"\nVerification: Found {len(themes)} themes in database:")
        for theme in themes:
            logger.info(f"  - {theme.name}: {theme.display_name} "
                       f"({theme.dimensions_width}x{theme.dimensions_height}, "
                       f"max {theme.max_entities} entities)")
        return len(themes) > 0
    except Exception as e:
        logger.error(f"Error verifying themes: {e}")
        return False
    finally:
        session.close()


def main():
    """Main entry point for theme seeding"""
    import os
    
    # Get database connection string from environment or use default
    db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/themed_animation')
    
    logger.info(f"Initializing database connection: {db_url}")
    
    try:
        # Initialize database
        init_db(db_url)
        
        # Create tables if they don't exist
        logger.info("Ensuring database tables exist...")
        create_all_tables()
        
        # Seed themes
        logger.info("Seeding themes...")
        success = seed_themes()
        
        if success:
            # Verify
            logger.info("\nVerifying themes...")
            verify_themes()
            logger.info("\n✓ Theme seeding completed successfully!")
        else:
            logger.error("\n✗ Theme seeding failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
