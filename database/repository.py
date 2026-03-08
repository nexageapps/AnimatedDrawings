"""
Base Repository Pattern for Data Access

Provides a clean abstraction layer for database operations using SQLAlchemy ORM.

Requirements: 9.2
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging

from database.orm import (
    get_session, User, Theme, ThemedWorld, Drawing, AnimationData,
    DrawingEntity, ProcessingJob, Notification, SystemLog
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations
    
    This implements the Repository pattern to abstract database access
    and provide a clean interface for domain operations.
    """
    
    def __init__(self, model_class: type):
        """
        Initialize repository
        
        Args:
            model_class: SQLAlchemy model class
        """
        self.model_class = model_class
    
    @contextmanager
    def _get_session(self, session: Optional[Session] = None):
        """
        Get a session, either provided or create a new one
        
        Args:
            session: Optional existing session
            
        Yields:
            Session instance
        """
        if session:
            yield session
        else:
            new_session = get_session()
            try:
                yield new_session
                new_session.commit()
            except Exception:
                new_session.rollback()
                raise
            finally:
                new_session.close()
    
    def create(self, entity: T, session: Optional[Session] = None) -> T:
        """
        Create a new entity
        
        Args:
            entity: Entity instance to create
            session: Optional session to use
            
        Returns:
            Created entity with ID populated
        """
        with self._get_session(session) as s:
            s.add(entity)
            s.flush()
            s.refresh(entity)
            return entity
    
    def get_by_id(self, entity_id: str, session: Optional[Session] = None) -> Optional[T]:
        """
        Get entity by ID
        
        Args:
            entity_id: Entity UUID
            session: Optional session to use
            
        Returns:
            Entity if found, None otherwise
        """
        with self._get_session(session) as s:
            return s.query(self.model_class).filter_by(id=entity_id).first()
    
    def get_all(self, session: Optional[Session] = None) -> List[T]:
        """
        Get all entities
        
        Args:
            session: Optional session to use
            
        Returns:
            List of all entities
        """
        with self._get_session(session) as s:
            return s.query(self.model_class).all()
    
    def find_by(self, filters: Dict[str, Any], session: Optional[Session] = None) -> List[T]:
        """
        Find entities by filters
        
        Args:
            filters: Dictionary of field names and values
            session: Optional session to use
            
        Returns:
            List of matching entities
        """
        with self._get_session(session) as s:
            query = s.query(self.model_class)
            for key, value in filters.items():
                query = query.filter(getattr(self.model_class, key) == value)
            return query.all()
    
    def find_one_by(self, filters: Dict[str, Any], session: Optional[Session] = None) -> Optional[T]:
        """
        Find single entity by filters
        
        Args:
            filters: Dictionary of field names and values
            session: Optional session to use
            
        Returns:
            First matching entity or None
        """
        with self._get_session(session) as s:
            query = s.query(self.model_class)
            for key, value in filters.items():
                query = query.filter(getattr(self.model_class, key) == value)
            return query.first()
    
    def update(self, entity_id: str, updates: Dict[str, Any], session: Optional[Session] = None) -> Optional[T]:
        """
        Update entity by ID
        
        Args:
            entity_id: Entity UUID
            updates: Dictionary of fields to update
            session: Optional session to use
            
        Returns:
            Updated entity if found, None otherwise
        """
        with self._get_session(session) as s:
            entity = s.query(self.model_class).filter_by(id=entity_id).first()
            if entity:
                for key, value in updates.items():
                    setattr(entity, key, value)
                s.flush()
                s.refresh(entity)
            return entity
    
    def delete(self, entity_id: str, session: Optional[Session] = None) -> bool:
        """
        Delete entity by ID
        
        Args:
            entity_id: Entity UUID
            session: Optional session to use
            
        Returns:
            True if deleted, False if not found
        """
        with self._get_session(session) as s:
            entity = s.query(self.model_class).filter_by(id=entity_id).first()
            if entity:
                s.delete(entity)
                return True
            return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None, session: Optional[Session] = None) -> int:
        """
        Count entities matching filters
        
        Args:
            filters: Optional dictionary of field names and values
            session: Optional session to use
            
        Returns:
            Count of matching entities
        """
        with self._get_session(session) as s:
            query = s.query(self.model_class)
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.model_class, key) == value)
            return query.count()


class UserRepository(BaseRepository[User]):
    """Repository for User entities"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email: str, session: Optional[Session] = None) -> Optional[User]:
        """Get user by email address"""
        return self.find_one_by({'email': email}, session)
    
    def increment_drawing_count(self, user_id: str, session: Optional[Session] = None) -> Optional[User]:
        """Increment user's total drawing count"""
        with self._get_session(session) as s:
            user = s.query(User).filter_by(id=user_id).first()
            if user:
                user.total_drawings += 1
                s.flush()
                s.refresh(user)
            return user


class ThemeRepository(BaseRepository[Theme]):
    """Repository for Theme entities"""
    
    def __init__(self):
        super().__init__(Theme)
    
    def get_by_name(self, name: str, session: Optional[Session] = None) -> Optional[Theme]:
        """Get theme by name"""
        return self.find_one_by({'name': name}, session)


class ThemedWorldRepository(BaseRepository[ThemedWorld]):
    """Repository for ThemedWorld entities"""
    
    def __init__(self):
        super().__init__(ThemedWorld)
    
    def get_by_theme(self, theme_id: str, session: Optional[Session] = None) -> List[ThemedWorld]:
        """Get all worlds for a theme"""
        return self.find_by({'theme_id': theme_id}, session)
    
    def get_available_world(self, theme_id: str, session: Optional[Session] = None) -> Optional[ThemedWorld]:
        """Get first available (not full) world for a theme"""
        with self._get_session(session) as s:
            return s.query(ThemedWorld).filter_by(
                theme_id=theme_id,
                is_full=False
            ).first()
    
    def increment_entity_count(self, world_id: str, session: Optional[Session] = None) -> Optional[ThemedWorld]:
        """Increment world's entity count"""
        with self._get_session(session) as s:
            world = s.query(ThemedWorld).filter_by(id=world_id).first()
            if world:
                world.entity_count += 1
                s.flush()
                s.refresh(world)
            return world


class DrawingRepository(BaseRepository[Drawing]):
    """Repository for Drawing entities"""
    
    def __init__(self):
        super().__init__(Drawing)
    
    def get_by_user(self, user_id: str, session: Optional[Session] = None) -> List[Drawing]:
        """Get all drawings for a user"""
        return self.find_by({'user_id': user_id}, session)
    
    def get_by_theme(self, theme_id: str, session: Optional[Session] = None) -> List[Drawing]:
        """Get all drawings for a theme"""
        return self.find_by({'theme_id': theme_id}, session)
    
    def get_by_status(self, status: str, session: Optional[Session] = None) -> List[Drawing]:
        """Get all drawings with a specific status"""
        return self.find_by({'status': status}, session)


class AnimationDataRepository(BaseRepository[AnimationData]):
    """Repository for AnimationData entities"""
    
    def __init__(self):
        super().__init__(AnimationData)
    
    def get_by_drawing(self, drawing_id: str, session: Optional[Session] = None) -> Optional[AnimationData]:
        """Get animation data for a drawing"""
        return self.find_one_by({'drawing_id': drawing_id}, session)


class DrawingEntityRepository(BaseRepository[DrawingEntity]):
    """Repository for DrawingEntity entities"""
    
    def __init__(self):
        super().__init__(DrawingEntity)
    
    def get_by_world(self, world_id: str, session: Optional[Session] = None) -> List[DrawingEntity]:
        """Get all entities in a world"""
        return self.find_by({'world_id': world_id}, session)
    
    def get_by_drawing(self, drawing_id: str, session: Optional[Session] = None) -> List[DrawingEntity]:
        """Get all entities for a drawing"""
        return self.find_by({'drawing_id': drawing_id}, session)


class ProcessingJobRepository(BaseRepository[ProcessingJob]):
    """Repository for ProcessingJob entities"""
    
    def __init__(self):
        super().__init__(ProcessingJob)
    
    def get_by_status(self, status: str, session: Optional[Session] = None) -> List[ProcessingJob]:
        """Get all jobs with a specific status"""
        return self.find_by({'status': status}, session)
    
    def get_by_drawing(self, drawing_id: str, session: Optional[Session] = None) -> List[ProcessingJob]:
        """Get all jobs for a drawing"""
        return self.find_by({'drawing_id': drawing_id}, session)
    
    def get_queued_jobs(self, session: Optional[Session] = None) -> List[ProcessingJob]:
        """Get all queued jobs ordered by priority and creation time"""
        with self._get_session(session) as s:
            return s.query(ProcessingJob).filter_by(
                status='queued'
            ).order_by(
                ProcessingJob.priority.desc(),
                ProcessingJob.created_at.asc()
            ).all()


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification entities"""
    
    def __init__(self):
        super().__init__(Notification)
    
    def get_by_user(self, user_id: str, session: Optional[Session] = None) -> List[Notification]:
        """Get all notifications for a user"""
        return self.find_by({'user_id': user_id}, session)
    
    def get_by_drawing(self, drawing_id: str, session: Optional[Session] = None) -> List[Notification]:
        """Get all notifications for a drawing"""
        return self.find_by({'drawing_id': drawing_id}, session)


class SystemLogRepository(BaseRepository[SystemLog]):
    """Repository for SystemLog entities"""
    
    def __init__(self):
        super().__init__(SystemLog)
    
    def get_by_level(self, level: str, session: Optional[Session] = None) -> List[SystemLog]:
        """Get all logs of a specific level"""
        return self.find_by({'level': level}, session)
    
    def get_by_component(self, component: str, session: Optional[Session] = None) -> List[SystemLog]:
        """Get all logs for a specific component"""
        return self.find_by({'component': component}, session)


# Singleton repository instances
user_repository = UserRepository()
theme_repository = ThemeRepository()
themed_world_repository = ThemedWorldRepository()
drawing_repository = DrawingRepository()
animation_data_repository = AnimationDataRepository()
drawing_entity_repository = DrawingEntityRepository()
processing_job_repository = ProcessingJobRepository()
notification_repository = NotificationRepository()
system_log_repository = SystemLogRepository()
