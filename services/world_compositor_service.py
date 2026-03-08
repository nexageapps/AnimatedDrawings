"""
World Compositor Service

Manages spatial positioning of drawing entities within themed worlds.
Implements grid-based collision detection and optimal placement algorithms
with theme-specific positioning rules.

Requirements: 5.1, 5.2, 5.3, 6.1, 6.5
"""

import logging
import math
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from uuid import uuid4

from models.themed_world import ThemedWorld
from models.drawing_entity import DrawingEntity
from models.theme import Theme
from database.orm import ThemedWorld as ThemedWorldORM, DrawingEntity as DrawingEntityORM, get_session
from services.positioning_rules import get_positioning_rules

logger = logging.getLogger(__name__)


class WorldCompositorService:
    """
    Service for managing spatial positioning of drawing entities in themed worlds.
    
    Implements:
    - Grid-based collision detection
    - Position scoring algorithm for optimal placement
    - Minimum spacing enforcement (50 pixels)
    - Theme-specific positioning rules
    """
    
    # Minimum spacing between entities in pixels (Requirement 5.3)
    MIN_SPACING = 50
    
    # Grid step size for position search (pixels)
    GRID_STEP = 25
    
    def __init__(self):
        """Initialize the World Compositor Service"""
        pass
    
    def calculate_position(
        self,
        world: ThemedWorld,
        theme: Theme,
        entity_width: int,
        entity_height: int,
        existing_entities: Optional[List[DrawingEntity]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Calculate optimal position for a new entity in the world.
        
        Uses grid-based search with collision detection and position scoring
        to find the best placement for the entity. Applies theme-specific
        positioning rules to create contextually appropriate placements.
        
        Args:
            world: ThemedWorld instance
            theme: Theme configuration with dimensions
            entity_width: Width of entity to place (pixels)
            entity_height: Height of entity to place (pixels)
            existing_entities: List of entities already in the world (optional)
            
        Returns:
            Tuple of (x, y) coordinates if valid position found, None otherwise
            
        Requirements: 5.1, 5.2, 5.3, 6.1, 6.5
        """
        if existing_entities is None:
            existing_entities = []
        
        world_width, world_height = theme.dimensions
        
        # Validate entity fits in world
        if entity_width > world_width or entity_height > world_height:
            logger.warning(
                f"Entity ({entity_width}x{entity_height}) too large for world "
                f"({world_width}x{world_height})"
            )
            return None
        
        # Get theme-specific positioning rules
        positioning_rules = get_positioning_rules(theme.name)
        constraints = positioning_rules.get_position_constraints(
            entity_width, entity_height, world_width, world_height, existing_entities
        )
        
        logger.info(f"Using {positioning_rules.__class__.__name__} for theme '{theme.name}'")
        
        # Build occupancy grid for fast collision detection
        grid = self._build_occupancy_grid(
            existing_entities,
            world_width,
            world_height,
            self.GRID_STEP
        )
        
        # Search for valid positions
        candidates = []
        
        for x in range(0, world_width - entity_width, self.GRID_STEP):
            for y in range(0, world_height - entity_height, self.GRID_STEP):
                # Check if position is valid (no collisions)
                if not self._is_position_valid(
                    x, y, entity_width, entity_height,
                    existing_entities, world_width, world_height
                ):
                    continue
                
                # Check theme-specific constraints
                if not positioning_rules.is_valid_position(
                    x, y, entity_width, entity_height,
                    world_width, world_height, constraints
                ):
                    continue
                
                # Calculate base score for this position
                base_score = self._calculate_position_score(
                    x, y, entity_width, entity_height,
                    existing_entities, world_width, world_height
                )
                
                # Apply theme-specific score adjustments
                adjusted_score = positioning_rules.adjust_position_score(
                    base_score, x, y, entity_width, entity_height,
                    world_width, world_height, existing_entities, constraints
                )
                
                candidates.append((adjusted_score, (x, y)))
        
        if not candidates:
            logger.warning("No valid positions found for entity placement")
            return None
        
        # Sort by score (higher is better) and return best position
        candidates.sort(reverse=True, key=lambda item: item[0])
        best_score, best_position = candidates[0]
        
        logger.info(
            f"Found optimal position {best_position} with score {best_score:.2f}"
        )
        
        return best_position
    
    def _build_occupancy_grid(
        self,
        entities: List[DrawingEntity],
        world_width: int,
        world_height: int,
        grid_step: int
    ) -> Dict[Tuple[int, int], bool]:
        """
        Build a grid representing occupied spaces in the world.
        
        Args:
            entities: List of existing entities
            world_width: Width of world
            world_height: Height of world
            grid_step: Size of grid cells
            
        Returns:
            Dictionary mapping (grid_x, grid_y) to occupancy boolean
        """
        grid = {}
        
        for entity in entities:
            # Mark all grid cells occupied by this entity (with spacing)
            x1 = max(0, entity.x - self.MIN_SPACING)
            y1 = max(0, entity.y - self.MIN_SPACING)
            x2 = min(world_width, entity.x + entity.width + self.MIN_SPACING)
            y2 = min(world_height, entity.y + entity.height + self.MIN_SPACING)
            
            # Convert to grid coordinates
            grid_x1 = x1 // grid_step
            grid_y1 = y1 // grid_step
            grid_x2 = (x2 + grid_step - 1) // grid_step
            grid_y2 = (y2 + grid_step - 1) // grid_step
            
            for gx in range(grid_x1, grid_x2 + 1):
                for gy in range(grid_y1, grid_y2 + 1):
                    grid[(gx, gy)] = True
        
        return grid
    
    def _is_position_valid(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        existing_entities: List[DrawingEntity],
        world_width: int,
        world_height: int
    ) -> bool:
        """
        Check if a position is valid (no collisions, within bounds).
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Entity width
            height: Entity height
            existing_entities: List of existing entities
            world_width: World width
            world_height: World height
            
        Returns:
            True if position is valid, False otherwise
            
        Requirements: 5.3 (minimum spacing enforcement)
        """
        # Check world bounds
        if x < 0 or y < 0:
            return False
        if x + width > world_width or y + height > world_height:
            return False
        
        # Check collisions with existing entities
        for entity in existing_entities:
            if self._check_collision(
                x, y, width, height,
                entity.x, entity.y, entity.width, entity.height,
                self.MIN_SPACING
            ):
                return False
        
        return True
    
    def _check_collision(
        self,
        x1: int, y1: int, w1: int, h1: int,
        x2: int, y2: int, w2: int, h2: int,
        min_spacing: int
    ) -> bool:
        """
        Check if two rectangles collide with minimum spacing.
        
        Args:
            x1, y1, w1, h1: First rectangle (x, y, width, height)
            x2, y2, w2, h2: Second rectangle (x, y, width, height)
            min_spacing: Minimum spacing required between rectangles
            
        Returns:
            True if rectangles collide (within min_spacing), False otherwise
        """
        # Expand first rectangle by min_spacing
        expanded_x1 = x1 - min_spacing
        expanded_y1 = y1 - min_spacing
        expanded_x2 = x1 + w1 + min_spacing
        expanded_y2 = y1 + h1 + min_spacing
        
        # Check for overlap
        if expanded_x2 < x2 or x2 + w2 < expanded_x1:
            return False
        if expanded_y2 < y2 or y2 + h2 < expanded_y1:
            return False
        
        return True
    
    def _calculate_position_score(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        existing_entities: List[DrawingEntity],
        world_width: int,
        world_height: int
    ) -> float:
        """
        Calculate a score for a position to determine optimal placement.
        
        Higher scores indicate better positions. Scoring considers:
        - Distance from other entities (prefer more spacing)
        - Distribution balance (prefer filling empty areas)
        - Center bias (slight preference for center positions)
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Entity width
            height: Entity height
            existing_entities: List of existing entities
            world_width: World width
            world_height: World height
            
        Returns:
            Score value (higher is better)
            
        Requirements: 6.1 (consider entity dimensions for optimal placement)
        """
        score = 0.0
        
        # Calculate center of new entity
        center_x = x + width / 2
        center_y = y + height / 2
        
        # 1. Distance from other entities (prefer more spacing)
        if existing_entities:
            min_distance = float('inf')
            avg_distance = 0.0
            
            for entity in existing_entities:
                entity_center_x = entity.x + entity.width / 2
                entity_center_y = entity.y + entity.height / 2
                
                distance = math.sqrt(
                    (center_x - entity_center_x) ** 2 +
                    (center_y - entity_center_y) ** 2
                )
                
                min_distance = min(min_distance, distance)
                avg_distance += distance
            
            avg_distance /= len(existing_entities)
            
            # Reward positions with good spacing
            score += min_distance * 0.5  # Weight for minimum distance
            score += avg_distance * 0.3   # Weight for average distance
        else:
            # First entity - prefer center
            score += 1000.0
        
        # 2. Distribution balance (prefer filling empty areas)
        # Divide world into quadrants and check occupancy
        world_center_x = world_width / 2
        world_center_y = world_height / 2
        
        # Determine which quadrant this position is in
        in_left = center_x < world_center_x
        in_top = center_y < world_center_y
        
        # Count entities in same quadrant
        same_quadrant_count = 0
        for entity in existing_entities:
            entity_center_x = entity.x + entity.width / 2
            entity_center_y = entity.y + entity.height / 2
            
            entity_in_left = entity_center_x < world_center_x
            entity_in_top = entity_center_y < world_center_y
            
            if entity_in_left == in_left and entity_in_top == in_top:
                same_quadrant_count += 1
        
        # Prefer quadrants with fewer entities (balanced distribution)
        score -= same_quadrant_count * 50.0
        
        # 3. Slight center bias (prefer positions not too close to edges)
        distance_from_center = math.sqrt(
            (center_x - world_center_x) ** 2 +
            (center_y - world_center_y) ** 2
        )
        max_distance = math.sqrt(world_center_x ** 2 + world_center_y ** 2)
        center_score = (1.0 - distance_from_center / max_distance) * 100.0
        score += center_score * 0.2  # Small weight for center bias
        
        return score
    
    def get_world_entities(self, world_id: str) -> List[DrawingEntity]:
        """
        Retrieve all entities in a world from the database.
        
        Args:
            world_id: World UUID
            
        Returns:
            List of DrawingEntity objects
        """
        session = get_session()
        try:
            entities_orm = session.query(DrawingEntityORM).filter_by(
                world_id=world_id
            ).all()
            
            return [self._entity_orm_to_domain(e) for e in entities_orm]
        except Exception as e:
            logger.error(f"Error retrieving entities for world {world_id}: {e}")
            return []
        finally:
            session.close()
    
    def place_entity(
        self,
        world_id: str,
        drawing_id: str,
        position: Tuple[int, int],
        dimensions: Tuple[int, int],
        z_index: int = 0
    ) -> Optional[DrawingEntity]:
        """
        Place a drawing entity at a specific position in a world.
        
        Args:
            world_id: World UUID
            drawing_id: Drawing UUID
            position: (x, y) coordinates
            dimensions: (width, height) of entity
            z_index: Z-order for layering (default: 0)
            
        Returns:
            Created DrawingEntity if successful, None otherwise
        """
        session = get_session()
        try:
            # Create entity
            entity_id = str(uuid4())
            entity = DrawingEntity(
                id=entity_id,
                drawing_id=drawing_id,
                world_id=world_id,
                position=position,
                z_index=z_index,
                dimensions=dimensions,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            entity_orm = self._entity_domain_to_orm(entity)
            session.add(entity_orm)
            
            # Update world entity count
            world_orm = session.query(ThemedWorldORM).filter_by(id=world_id).first()
            if world_orm:
                world_orm.entity_count += 1
                world_orm.last_updated = datetime.utcnow()
            
            session.commit()
            
            logger.info(
                f"Placed entity {entity_id} at position {position} in world {world_id}"
            )
            
            return entity
        except Exception as e:
            session.rollback()
            logger.error(f"Error placing entity: {e}")
            return None
        finally:
            session.close()
    
    def _entity_orm_to_domain(self, entity_orm: DrawingEntityORM) -> DrawingEntity:
        """Convert ORM model to domain model"""
        return DrawingEntity(
            id=str(entity_orm.id),
            drawing_id=str(entity_orm.drawing_id),
            world_id=str(entity_orm.world_id),
            position=(entity_orm.position_x, entity_orm.position_y),
            z_index=entity_orm.z_index,
            dimensions=(entity_orm.width, entity_orm.height),
            created_at=entity_orm.created_at
        )
    
    def _entity_domain_to_orm(self, entity: DrawingEntity) -> DrawingEntityORM:
        """Convert domain model to ORM model"""
        entity_orm = DrawingEntityORM()
        entity_orm.id = entity.id
        entity_orm.drawing_id = entity.drawing_id
        entity_orm.world_id = entity.world_id
        entity_orm.position_x = entity.position[0]
        entity_orm.position_y = entity.position[1]
        entity_orm.z_index = entity.z_index
        entity_orm.width = entity.dimensions[0]
        entity_orm.height = entity.dimensions[1]
        entity_orm.created_at = entity.created_at
        return entity_orm
