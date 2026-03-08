"""
Positioning Rules for Themed Worlds

Implements theme-specific positioning strategies for placing drawing entities
in themed worlds. Each theme has unique positioning rules that create
contextually appropriate spatial arrangements.

Requirements: 5.1, 6.5
"""

import random
import math
from typing import Tuple, List, Optional
from abc import ABC, abstractmethod

from models.drawing_entity import DrawingEntity


class PositioningRules(ABC):
    """
    Abstract base class for theme-specific positioning rules.
    
    Each theme implements its own positioning strategy by subclassing
    this base class and implementing the constraint methods.
    """
    
    @abstractmethod
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """
        Get positioning constraints for this theme.
        
        Returns a dictionary with constraint parameters that will be used
        to filter and score candidate positions.
        
        Args:
            entity_width: Width of entity to place
            entity_height: Height of entity to place
            world_width: Width of world
            world_height: Height of world
            existing_entities: List of entities already in world
            
        Returns:
            Dictionary with constraint parameters
        """
        pass
    
    @abstractmethod
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """
        Check if a position satisfies theme-specific constraints.
        
        Args:
            x: X coordinate
            y: Y coordinate
            entity_width: Width of entity
            entity_height: Height of entity
            world_width: Width of world
            world_height: Height of world
            constraints: Constraint parameters from get_position_constraints
            
        Returns:
            True if position is valid for this theme, False otherwise
        """
        pass
    
    @abstractmethod
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """
        Adjust position score based on theme-specific preferences.
        
        Args:
            base_score: Base score from general positioning algorithm
            x: X coordinate
            y: Y coordinate
            entity_width: Width of entity
            entity_height: Height of entity
            world_width: Width of world
            world_height: Height of world
            existing_entities: List of entities already in world
            constraints: Constraint parameters from get_position_constraints
            
        Returns:
            Adjusted score (can be higher or lower than base_score)
        """
        pass


class JunglePositioningRules(PositioningRules):
    """
    Jungle theme positioning: Ground-based with vertical layering for depth.
    
    Entities are positioned on the ground (bottom portion of world) with
    vertical layering to create depth perception. Smaller entities can be
    placed higher to simulate distance.
    """
    
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """Get jungle positioning constraints."""
        # Ground level is bottom 70% of world
        ground_level_start = int(world_height * 0.3)
        
        return {
            'ground_level_start': ground_level_start,
            'ground_level_end': world_height,
            'allow_elevated': entity_height < 100,  # Small entities can be elevated
        }
    
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """Check if position is valid for jungle theme."""
        # Entity bottom should be in ground level range
        entity_bottom = y + entity_height
        
        if constraints['allow_elevated']:
            # Small entities can be anywhere in bottom 70%
            return entity_bottom >= constraints['ground_level_start']
        else:
            # Large entities must be on ground (bottom 30%)
            return y >= constraints['ground_level_start']
    
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """Adjust score to prefer ground-based positioning."""
        score = base_score
        
        # Prefer positions closer to ground
        entity_bottom = y + entity_height
        distance_from_ground = world_height - entity_bottom
        ground_preference = (1.0 - distance_from_ground / world_height) * 100.0
        score += ground_preference
        
        # Vertical layering: prefer spreading entities across different heights
        # to create depth
        if existing_entities:
            # Count entities at similar height
            similar_height_count = 0
            for entity in existing_entities:
                if abs(entity.y - y) < 50:
                    similar_height_count += 1
            
            # Penalize crowded heights
            score -= similar_height_count * 20.0
        
        return score


class ChristmasPositioningRules(PositioningRules):
    """
    Christmas theme positioning: Clustered around center with some floating.
    
    Entities cluster around the center (like ornaments on a tree) with
    some entities floating higher (like tree toppers or stars).
    """
    
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """Get christmas positioning constraints."""
        center_x = world_width // 2
        center_y = world_height // 2
        
        # Cluster radius increases with number of entities
        base_radius = min(world_width, world_height) * 0.3
        entity_count = len(existing_entities)
        cluster_radius = base_radius + (entity_count * 10)
        
        return {
            'center_x': center_x,
            'center_y': center_y,
            'cluster_radius': cluster_radius,
            'allow_floating': random.random() < 0.3,  # 30% chance to float
        }
    
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """Check if position is valid for christmas theme."""
        # Calculate entity center
        entity_center_x = x + entity_width // 2
        entity_center_y = y + entity_height // 2
        
        # Calculate distance from world center
        distance = math.sqrt(
            (entity_center_x - constraints['center_x']) ** 2 +
            (entity_center_y - constraints['center_y']) ** 2
        )
        
        # Allow floating entities anywhere, others must be in cluster
        if constraints['allow_floating']:
            return True
        else:
            return distance <= constraints['cluster_radius']
    
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """Adjust score to prefer clustered positioning."""
        score = base_score
        
        # Calculate entity center
        entity_center_x = x + entity_width // 2
        entity_center_y = y + entity_height // 2
        
        # Calculate distance from world center
        distance = math.sqrt(
            (entity_center_x - constraints['center_x']) ** 2 +
            (entity_center_y - constraints['center_y']) ** 2
        )
        
        if constraints['allow_floating']:
            # Floating entities prefer top area
            if y < world_height * 0.3:
                score += 150.0
        else:
            # Clustered entities prefer being closer to center
            max_distance = math.sqrt(world_width ** 2 + world_height ** 2) / 2
            center_preference = (1.0 - distance / max_distance) * 200.0
            score += center_preference
        
        return score


class PartyPositioningRules(PositioningRules):
    """
    Party theme positioning: Random distribution with some elevated.
    
    Entities are randomly distributed across the world with some
    elevated positions (like balloons floating up).
    """
    
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """Get party positioning constraints."""
        return {
            'is_elevated': random.random() < 0.4,  # 40% chance to be elevated
            'elevation_zone_end': int(world_height * 0.4),  # Top 40% for elevated
        }
    
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """Check if position is valid for party theme."""
        # All positions are valid (random distribution)
        # But elevated entities prefer top area
        if constraints['is_elevated']:
            return y <= constraints['elevation_zone_end']
        return True
    
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """Adjust score for random distribution."""
        score = base_score
        
        # Add randomness to encourage varied placement
        random_factor = random.uniform(-50.0, 50.0)
        score += random_factor
        
        # Elevated entities prefer top area
        if constraints['is_elevated']:
            if y < constraints['elevation_zone_end']:
                score += 100.0
            else:
                score -= 100.0
        
        return score


class SchoolPositioningRules(PositioningRules):
    """
    School theme positioning: Row-based structured layout.
    
    Entities are arranged in rows (like desks in a classroom) with
    structured spacing and alignment.
    """
    
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """Get school positioning constraints."""
        # Define row parameters
        row_height = 150  # Height of each row
        num_rows = world_height // row_height
        entities_per_row = world_width // 200  # Approximate spacing
        
        # Calculate which row to place in
        current_entity_count = len(existing_entities)
        target_row = (current_entity_count // entities_per_row) % num_rows
        target_col = current_entity_count % entities_per_row
        
        return {
            'row_height': row_height,
            'num_rows': num_rows,
            'entities_per_row': entities_per_row,
            'target_row': target_row,
            'target_col': target_col,
        }
    
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """Check if position is valid for school theme."""
        # Position should be in target row (with some tolerance)
        row_start = constraints['target_row'] * constraints['row_height']
        row_end = row_start + constraints['row_height']
        
        # Allow some flexibility in row placement
        return row_start - 50 <= y <= row_end + 50
    
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """Adjust score to prefer row-based positioning."""
        score = base_score
        
        # Calculate ideal position for this entity
        row_start = constraints['target_row'] * constraints['row_height']
        ideal_y = row_start + (constraints['row_height'] - entity_height) // 2
        
        col_spacing = world_width // (constraints['entities_per_row'] + 1)
        ideal_x = (constraints['target_col'] + 1) * col_spacing - entity_width // 2
        
        # Reward positions close to ideal
        distance_from_ideal = math.sqrt(
            (x - ideal_x) ** 2 + (y - ideal_y) ** 2
        )
        alignment_bonus = max(0, 300.0 - distance_from_ideal)
        score += alignment_bonus
        
        # Bonus for being aligned with row
        y_alignment = abs(y - ideal_y)
        if y_alignment < 20:
            score += 100.0
        
        return score


class OceanPositioningRules(PositioningRules):
    """
    Ocean theme positioning: Depth-based layers with floating positions.
    
    Entities are arranged in depth layers (foreground, midground, background)
    with floating/swimming positions throughout the water column.
    """
    
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """Get ocean positioning constraints."""
        # Define depth layers
        # Surface: top 20%
        # Mid-water: 20-60%
        # Deep: 60-100%
        
        # Randomly assign depth layer
        depth_choice = random.random()
        if depth_choice < 0.3:
            layer = 'surface'
            layer_start = 0
            layer_end = int(world_height * 0.2)
        elif depth_choice < 0.7:
            layer = 'mid'
            layer_start = int(world_height * 0.2)
            layer_end = int(world_height * 0.6)
        else:
            layer = 'deep'
            layer_start = int(world_height * 0.6)
            layer_end = world_height
        
        return {
            'layer': layer,
            'layer_start': layer_start,
            'layer_end': layer_end,
        }
    
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """Check if position is valid for ocean theme."""
        # Entity should be within its assigned depth layer
        entity_center_y = y + entity_height // 2
        return constraints['layer_start'] <= entity_center_y <= constraints['layer_end']
    
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """Adjust score for depth-based positioning."""
        score = base_score
        
        # Calculate entity center
        entity_center_y = y + entity_height // 2
        
        # Reward positions in the middle of the assigned layer
        layer_middle = (constraints['layer_start'] + constraints['layer_end']) // 2
        distance_from_layer_middle = abs(entity_center_y - layer_middle)
        layer_height = constraints['layer_end'] - constraints['layer_start']
        
        if layer_height > 0:
            layer_preference = (1.0 - distance_from_layer_middle / layer_height) * 150.0
            score += layer_preference
        
        # Count entities in same layer for distribution
        same_layer_count = 0
        for entity in existing_entities:
            entity_center = entity.y + entity.height // 2
            if constraints['layer_start'] <= entity_center <= constraints['layer_end']:
                same_layer_count += 1
        
        # Slight penalty for crowded layers
        score -= same_layer_count * 10.0
        
        return score


class GeneralPositioningRules(PositioningRules):
    """
    General/default theme positioning: Balanced grid distribution.
    
    Entities are distributed evenly across the world using a balanced
    grid approach without specific theme constraints.
    """
    
    def get_position_constraints(
        self,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity]
    ) -> dict:
        """Get general positioning constraints."""
        return {}  # No special constraints
    
    def is_valid_position(
        self,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        constraints: dict
    ) -> bool:
        """Check if position is valid for general theme."""
        return True  # All positions are valid
    
    def adjust_position_score(
        self,
        base_score: float,
        x: int,
        y: int,
        entity_width: int,
        entity_height: int,
        world_width: int,
        world_height: int,
        existing_entities: List[DrawingEntity],
        constraints: dict
    ) -> float:
        """No adjustment for general theme."""
        return base_score  # Use base score as-is


def get_positioning_rules(theme_name: str) -> PositioningRules:
    """
    Factory function to get positioning rules for a theme.
    
    Args:
        theme_name: Name of the theme (e.g., 'jungle', 'christmas')
        
    Returns:
        PositioningRules instance for the theme
    """
    rules_map = {
        'jungle': JunglePositioningRules(),
        'christmas': ChristmasPositioningRules(),
        'party': PartyPositioningRules(),
        'school': SchoolPositioningRules(),
        'ocean': OceanPositioningRules(),
    }
    
    return rules_map.get(theme_name.lower(), GeneralPositioningRules())
