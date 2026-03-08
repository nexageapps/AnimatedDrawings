"""
Theme Manager Service

Manages theme operations including CRUD, validation, and theme-to-motion-sequence mapping.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 11.5
"""

import logging
import json
import os
from typing import Optional, List, Dict
from pathlib import Path

from models.theme import Theme
from database.orm import Theme as ThemeORM, get_session

logger = logging.getLogger(__name__)


class ThemeManagerService:
    """
    Service for managing themes in the Themed Animation Platform.
    
    Provides CRUD operations, validation, default theme logic, and
    theme-to-motion-sequence mapping.
    """
    
    DEFAULT_THEME_NAME = "general"
    
    # Theme-to-motion-sequence mapping as defined in design document
    THEME_MOTIONS = {
        'jungle': ['zombie', 'jumping', 'wave_hello'],
        'christmas': ['jesse_dance', 'wave_hello', 'dab'],
        'party': ['jesse_dance', 'jumping', 'dab', 'jumping_jacks'],
        'school': ['wave_hello', 'jumping', 'dab'],
        'ocean': ['wave_hello', 'zombie', 'jesse_dance'],
        'general': ['wave_hello', 'jumping', 'dab']
    }
    
    def __init__(self):
        """Initialize the Theme Manager Service"""
        self.config_dir = Path(__file__).parent.parent / 'config' / 'themes'
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """
        Retrieve theme configuration by name.
        
        Args:
            theme_name: Internal theme name (e.g., 'jungle', 'christmas')
            
        Returns:
            Theme object if found, None otherwise
            
        Requirements: 4.1
        """
        session = get_session()
        try:
            theme_orm = session.query(ThemeORM).filter_by(name=theme_name).first()
            if theme_orm:
                return self._orm_to_domain(theme_orm)
            return None
        except Exception as e:
            logger.error(f"Error retrieving theme '{theme_name}': {e}")
            return None
        finally:
            session.close()
    
    def get_theme_by_id(self, theme_id: str) -> Optional[Theme]:
        """
        Retrieve theme configuration by ID.
        
        Args:
            theme_id: Theme UUID
            
        Returns:
            Theme object if found, None otherwise
        """
        session = get_session()
        try:
            theme_orm = session.query(ThemeORM).filter_by(id=theme_id).first()
            if theme_orm:
                return self._orm_to_domain(theme_orm)
            return None
        except Exception as e:
            logger.error(f"Error retrieving theme by ID '{theme_id}': {e}")
            return None
        finally:
            session.close()
    
    def get_all_themes(self) -> List[Theme]:
        """
        Retrieve all available themes.
        
        Returns:
            List of Theme objects
        """
        session = get_session()
        try:
            themes_orm = session.query(ThemeORM).all()
            return [self._orm_to_domain(t) for t in themes_orm]
        except Exception as e:
            logger.error(f"Error retrieving all themes: {e}")
            return []
        finally:
            session.close()
    
    def validate_theme(self, theme_name: str) -> bool:
        """
        Check if theme exists in the system.
        
        Args:
            theme_name: Theme name to validate
            
        Returns:
            True if theme exists, False otherwise
            
        Requirements: 4.4
        """
        if not theme_name:
            return False
        
        session = get_session()
        try:
            count = session.query(ThemeORM).filter_by(name=theme_name).count()
            return count > 0
        except Exception as e:
            logger.error(f"Error validating theme '{theme_name}': {e}")
            return False
        finally:
            session.close()
    
    def get_default_theme(self) -> Theme:
        """
        Return the default theme.
        
        Returns:
            Default Theme object (general theme)
            
        Requirements: 4.3
        """
        theme = self.get_theme(self.DEFAULT_THEME_NAME)
        if theme is None:
            logger.error(f"Default theme '{self.DEFAULT_THEME_NAME}' not found in database!")
            raise RuntimeError(f"Default theme '{self.DEFAULT_THEME_NAME}' must exist in database")
        return theme
    
    def get_theme_properties(self, theme_name: str) -> Optional[Dict]:
        """
        Get theme-specific properties including dimensions, rules, and assets.
        
        Args:
            theme_name: Theme name
            
        Returns:
            Dictionary containing theme properties, or None if theme not found
            
        Requirements: 4.5
        """
        theme = self.get_theme(theme_name)
        if theme is None:
            return None
        
        return {
            'name': theme.name,
            'display_name': theme.display_name,
            'background_image_url': theme.background_image_url,
            'dimensions': theme.dimensions,
            'max_entities': theme.max_entities,
            'positioning_rules': theme.positioning_rules,
            'motion_sequences': theme.motion_sequences
        }
    
    def get_motion_sequences_for_theme(self, theme_name: str) -> List[str]:
        """
        Get the list of motion sequences appropriate for a theme.
        
        Args:
            theme_name: Theme name
            
        Returns:
            List of motion sequence names (BVH file names without extension)
            
        Requirements: 11.5
        """
        # First try to get from database
        theme = self.get_theme(theme_name)
        if theme and theme.motion_sequences:
            return theme.motion_sequences
        
        # Fallback to hardcoded mapping
        return self.THEME_MOTIONS.get(theme_name, self.THEME_MOTIONS[self.DEFAULT_THEME_NAME])
    
    def create_theme(self, theme: Theme) -> bool:
        """
        Create a new theme in the database.
        
        Args:
            theme: Theme domain model to create
            
        Returns:
            True if successful, False otherwise
        """
        session = get_session()
        try:
            # Check if theme already exists
            existing = session.query(ThemeORM).filter_by(name=theme.name).first()
            if existing:
                logger.warning(f"Theme '{theme.name}' already exists")
                return False
            
            # Create ORM object
            theme_orm = self._domain_to_orm(theme)
            session.add(theme_orm)
            session.commit()
            
            logger.info(f"Created theme '{theme.name}'")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating theme '{theme.name}': {e}")
            return False
        finally:
            session.close()
    
    def update_theme(self, theme: Theme) -> bool:
        """
        Update an existing theme in the database.
        
        Args:
            theme: Theme domain model with updated values
            
        Returns:
            True if successful, False otherwise
        """
        session = get_session()
        try:
            theme_orm = session.query(ThemeORM).filter_by(id=theme.id).first()
            if not theme_orm:
                logger.warning(f"Theme with ID '{theme.id}' not found")
                return False
            
            # Update fields
            theme_orm.name = theme.name
            theme_orm.display_name = theme.display_name
            theme_orm.background_image_url = theme.background_image_url
            theme_orm.dimensions_width = theme.dimensions[0]
            theme_orm.dimensions_height = theme.dimensions[1]
            theme_orm.max_entities = theme.max_entities
            theme_orm.positioning_rules = theme.positioning_rules
            theme_orm.motion_sequences = theme.motion_sequences
            
            session.commit()
            logger.info(f"Updated theme '{theme.name}'")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating theme '{theme.name}': {e}")
            return False
        finally:
            session.close()
    
    def delete_theme(self, theme_name: str) -> bool:
        """
        Delete a theme from the database.
        
        Args:
            theme_name: Name of theme to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Prevent deletion of default theme
        if theme_name == self.DEFAULT_THEME_NAME:
            logger.error(f"Cannot delete default theme '{self.DEFAULT_THEME_NAME}'")
            return False
        
        session = get_session()
        try:
            theme_orm = session.query(ThemeORM).filter_by(name=theme_name).first()
            if not theme_orm:
                logger.warning(f"Theme '{theme_name}' not found")
                return False
            
            session.delete(theme_orm)
            session.commit()
            logger.info(f"Deleted theme '{theme_name}'")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting theme '{theme_name}': {e}")
            return False
        finally:
            session.close()
    
    def _orm_to_domain(self, theme_orm: ThemeORM) -> Theme:
        """Convert ORM model to domain model"""
        return Theme(
            id=str(theme_orm.id),
            name=theme_orm.name,
            display_name=theme_orm.display_name,
            background_image_url=theme_orm.background_image_url or '',
            dimensions=(theme_orm.dimensions_width, theme_orm.dimensions_height),
            max_entities=theme_orm.max_entities,
            positioning_rules=theme_orm.positioning_rules or {},
            motion_sequences=theme_orm.motion_sequences or []
        )
    
    def _domain_to_orm(self, theme: Theme) -> ThemeORM:
        """Convert domain model to ORM model"""
        theme_orm = ThemeORM()
        if hasattr(theme, 'id') and theme.id:
            theme_orm.id = theme.id
        theme_orm.name = theme.name
        theme_orm.display_name = theme.display_name
        theme_orm.background_image_url = theme.background_image_url
        theme_orm.dimensions_width = theme.dimensions[0]
        theme_orm.dimensions_height = theme.dimensions[1]
        theme_orm.max_entities = theme.max_entities
        theme_orm.positioning_rules = theme.positioning_rules
        theme_orm.motion_sequences = theme.motion_sequences
        return theme_orm
