"""
Unit tests for domain models.

Tests validation logic and model behavior for all domain models.
"""

import pytest
from datetime import datetime, timedelta
from models import (
    User, Theme, ThemedWorld, Drawing, DrawingStatus,
    AnimationData, DrawingEntity, ProcessingJob, JobStatus
)


class TestUser:
    """Tests for User model."""
    
    def test_valid_user(self):
        """Test creating a valid user."""
        user = User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            created_at=datetime.now(),
            total_drawings=5
        )
        assert user.email == "test@example.com"
        assert user.total_drawings == 5
    
    def test_invalid_email_format(self):
        """Test that invalid email format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                id="123e4567-e89b-12d3-a456-426614174000",
                email="invalid-email",
                created_at=datetime.now(),
                total_drawings=0
            )
    
    def test_negative_total_drawings(self):
        """Test that negative total_drawings raises ValueError."""
        with pytest.raises(ValueError, match="total_drawings must be non-negative"):
            User(
                id="123e4567-e89b-12d3-a456-426614174000",
                email="test@example.com",
                created_at=datetime.now(),
                total_drawings=-1
            )


class TestDrawing:
    """Tests for Drawing model."""
    
    def test_valid_drawing(self):
        """Test creating a valid drawing."""
        drawing = Drawing(
            id="123e4567-e89b-12d3-a456-426614174000",
            user_id="user-123",
            original_image_url="/uploads/image.png",
            normalized_image_url="/uploads/normalized.png",
            status=DrawingStatus.ANIMATED,
            theme_id="theme-123",
            created_at=datetime.now(),
            processed_at=datetime.now(),
            error_message=None
        )
        assert drawing.status == DrawingStatus.ANIMATED
        assert drawing.is_successful()
        assert drawing.is_complete()
    
    def test_status_string_conversion(self):
        """Test that status string is converted to enum."""
        drawing = Drawing(
            id="123e4567-e89b-12d3-a456-426614174000",
            user_id="user-123",
            original_image_url="/uploads/image.png",
            normalized_image_url=None,
            status="pending",
            theme_id="theme-123",
            created_at=datetime.now(),
            processed_at=None,
            error_message=None
        )
        assert drawing.status == DrawingStatus.PENDING
        assert isinstance(drawing.status, DrawingStatus)
    
    def test_empty_image_url(self):
        """Test that empty image URL raises ValueError."""
        with pytest.raises(ValueError, match="original_image_url cannot be empty"):
            Drawing(
                id="123e4567-e89b-12d3-a456-426614174000",
                user_id="user-123",
                original_image_url="",
                normalized_image_url=None,
                status=DrawingStatus.PENDING,
                theme_id="theme-123",
                created_at=datetime.now(),
                processed_at=None,
                error_message=None
            )
    
    def test_failed_without_error_message(self):
        """Test that failed status requires error message."""
        with pytest.raises(ValueError, match="error_message is required"):
            Drawing(
                id="123e4567-e89b-12d3-a456-426614174000",
                user_id="user-123",
                original_image_url="/uploads/image.png",
                normalized_image_url=None,
                status=DrawingStatus.FAILED,
                theme_id="theme-123",
                created_at=datetime.now(),
                processed_at=None,
                error_message=None
            )


class TestTheme:
    """Tests for Theme model."""
    
    def test_valid_theme(self):
        """Test creating a valid theme."""
        theme = Theme(
            id="theme-123",
            name="jungle",
            display_name="Jungle Adventure",
            background_image_url="/static/backgrounds/jungle.png",
            dimensions=(1920, 1080),
            max_entities=50,
            positioning_rules={"type": "ground_based"},
            motion_sequences=["walk", "run", "climb"]
        )
        assert theme.name == "jungle"
        assert theme.width == 1920
        assert theme.height == 1080
        assert theme.has_motion_sequence("walk")
        assert not theme.has_motion_sequence("fly")
    
    def test_invalid_dimensions(self):
        """Test that invalid dimensions raise ValueError."""
        with pytest.raises(ValueError, match="dimensions must be positive"):
            Theme(
                id="theme-123",
                name="jungle",
                display_name="Jungle Adventure",
                background_image_url="/static/backgrounds/jungle.png",
                dimensions=(0, 1080),
                max_entities=50,
                positioning_rules={},
                motion_sequences=["walk"]
            )
    
    def test_empty_motion_sequences(self):
        """Test that empty motion sequences raise ValueError."""
        with pytest.raises(ValueError, match="motion_sequences cannot be empty"):
            Theme(
                id="theme-123",
                name="jungle",
                display_name="Jungle Adventure",
                background_image_url="/static/backgrounds/jungle.png",
                dimensions=(1920, 1080),
                max_entities=50,
                positioning_rules={},
                motion_sequences=[]
            )


class TestThemedWorld:
    """Tests for ThemedWorld model."""
    
    def test_valid_themed_world(self):
        """Test creating a valid themed world."""
        now = datetime.now()
        world = ThemedWorld(
            id="world-123",
            theme_id="theme-123",
            instance_number=1,
            entity_count=10,
            is_full=False,
            created_at=now,
            last_updated=now
        )
        assert world.instance_number == 1
        assert world.entity_count == 10
        assert world.can_add_entity(50)
        assert world.get_occupancy_rate(50) == 0.2
    
    def test_invalid_instance_number(self):
        """Test that invalid instance number raises ValueError."""
        with pytest.raises(ValueError, match="instance_number must be positive"):
            ThemedWorld(
                id="world-123",
                theme_id="theme-123",
                instance_number=0,
                entity_count=0,
                is_full=False,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
    
    def test_full_world_cannot_add_entity(self):
        """Test that full world cannot add entities."""
        world = ThemedWorld(
            id="world-123",
            theme_id="theme-123",
            instance_number=1,
            entity_count=50,
            is_full=True,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        assert not world.can_add_entity(50)


class TestAnimationData:
    """Tests for AnimationData model."""
    
    def test_valid_animation_data(self):
        """Test creating valid animation data."""
        anim = AnimationData(
            id="anim-123",
            drawing_id="drawing-123",
            character_detected=True,
            segmentation_mask_url="/masks/mask.png",
            skeleton_data={"joints": [1, 2, 3]},
            motion_sequence="walk",
            animation_file_url="/animations/anim.mp4",
            sprite_sheet_url="/sprites/sheet.png"
        )
        assert anim.character_detected
        assert anim.is_complete()
        assert anim.has_sprite_sheet()
    
    def test_character_detected_requires_fields(self):
        """Test that character_detected=True requires certain fields."""
        with pytest.raises(ValueError, match="segmentation_mask_url required"):
            AnimationData(
                id="anim-123",
                drawing_id="drawing-123",
                character_detected=True,
                segmentation_mask_url=None,
                skeleton_data={"joints": []},
                motion_sequence="walk",
                animation_file_url="/animations/anim.mp4",
                sprite_sheet_url=None
            )
    
    def test_no_character_detected(self):
        """Test animation data when no character detected."""
        anim = AnimationData(
            id="anim-123",
            drawing_id="drawing-123",
            character_detected=False,
            segmentation_mask_url=None,
            skeleton_data=None,
            motion_sequence=None,
            animation_file_url=None,
            sprite_sheet_url=None
        )
        assert not anim.character_detected
        assert not anim.is_complete()


class TestDrawingEntity:
    """Tests for DrawingEntity model."""
    
    def test_valid_drawing_entity(self):
        """Test creating a valid drawing entity."""
        entity = DrawingEntity(
            id="entity-123",
            drawing_id="drawing-123",
            world_id="world-123",
            position=(100, 200),
            z_index=1,
            dimensions=(150, 200),
            created_at=datetime.now()
        )
        assert entity.x == 100
        assert entity.y == 200
        assert entity.width == 150
        assert entity.height == 200
        assert entity.get_center() == (175.0, 300.0)
    
    def test_negative_position(self):
        """Test that negative position raises ValueError."""
        with pytest.raises(ValueError, match="position must be non-negative"):
            DrawingEntity(
                id="entity-123",
                drawing_id="drawing-123",
                world_id="world-123",
                position=(-10, 200),
                z_index=1,
                dimensions=(150, 200),
                created_at=datetime.now()
            )
    
    def test_distance_calculation(self):
        """Test distance calculation between entities."""
        entity1 = DrawingEntity(
            id="entity-1",
            drawing_id="drawing-1",
            world_id="world-123",
            position=(0, 0),
            z_index=1,
            dimensions=(100, 100),
            created_at=datetime.now()
        )
        entity2 = DrawingEntity(
            id="entity-2",
            drawing_id="drawing-2",
            world_id="world-123",
            position=(300, 400),
            z_index=1,
            dimensions=(100, 100),
            created_at=datetime.now()
        )
        # Centers are at (50, 50) and (350, 450)
        # Distance = sqrt((300)^2 + (400)^2) = 500
        assert entity1.distance_to(entity2) == 500.0
    
    def test_overlap_detection(self):
        """Test overlap detection between entities."""
        entity1 = DrawingEntity(
            id="entity-1",
            drawing_id="drawing-1",
            world_id="world-123",
            position=(0, 0),
            z_index=1,
            dimensions=(100, 100),
            created_at=datetime.now()
        )
        entity2 = DrawingEntity(
            id="entity-2",
            drawing_id="drawing-2",
            world_id="world-123",
            position=(50, 50),
            z_index=1,
            dimensions=(100, 100),
            created_at=datetime.now()
        )
        entity3 = DrawingEntity(
            id="entity-3",
            drawing_id="drawing-3",
            world_id="world-123",
            position=(200, 200),
            z_index=1,
            dimensions=(100, 100),
            created_at=datetime.now()
        )
        
        assert entity1.overlaps_with(entity2)
        assert not entity1.overlaps_with(entity3)
        
        # Test with minimum spacing
        assert entity1.overlaps_with(entity3, min_spacing=200)


class TestProcessingJob:
    """Tests for ProcessingJob model."""
    
    def test_valid_processing_job(self):
        """Test creating a valid processing job."""
        now = datetime.now()
        job = ProcessingJob(
            id="job-123",
            drawing_id="drawing-123",
            job_type="animation",
            status=JobStatus.QUEUED,
            priority=0,
            attempts=0,
            max_attempts=3,
            error_message=None,
            created_at=now,
            started_at=None,
            completed_at=None
        )
        assert job.job_type == "animation"
        assert job.status == JobStatus.QUEUED
        assert not job.is_complete()
        
        # Test retry logic for failed job
        failed_job = ProcessingJob(
            id="job-456",
            drawing_id="drawing-123",
            job_type="animation",
            status=JobStatus.FAILED,
            priority=0,
            attempts=1,
            max_attempts=3,
            error_message="Test error",
            created_at=now,
            started_at=None,
            completed_at=None
        )
        assert failed_job.can_retry()
        assert failed_job.should_retry()
    
    def test_status_string_conversion(self):
        """Test that status string is converted to enum."""
        job = ProcessingJob(
            id="job-123",
            drawing_id="drawing-123",
            job_type="animation",
            status="queued",
            priority=0,
            attempts=0,
            max_attempts=3,
            error_message=None,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None
        )
        assert job.status == JobStatus.QUEUED
        assert isinstance(job.status, JobStatus)
    
    def test_invalid_job_type(self):
        """Test that invalid job type raises ValueError."""
        with pytest.raises(ValueError, match="job_type must be one of"):
            ProcessingJob(
                id="job-123",
                drawing_id="drawing-123",
                job_type="invalid_type",
                status=JobStatus.QUEUED,
                priority=0,
                attempts=0,
                max_attempts=3,
                error_message=None,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None
            )
    
    def test_failed_job_requires_error_message(self):
        """Test that failed job requires error message."""
        with pytest.raises(ValueError, match="error_message is required"):
            ProcessingJob(
                id="job-123",
                drawing_id="drawing-123",
                job_type="animation",
                status=JobStatus.FAILED,
                priority=0,
                attempts=1,
                max_attempts=3,
                error_message=None,
                created_at=datetime.now(),
                started_at=None,
                completed_at=None
            )
    
    def test_processing_duration(self):
        """Test processing duration calculation."""
        now = datetime.now()
        started = now - timedelta(seconds=30)
        completed = now
        
        job = ProcessingJob(
            id="job-123",
            drawing_id="drawing-123",
            job_type="animation",
            status=JobStatus.COMPLETED,
            priority=0,
            attempts=1,
            max_attempts=3,
            error_message=None,
            created_at=now - timedelta(seconds=60),
            started_at=started,
            completed_at=completed
        )
        
        duration = job.get_processing_duration()
        assert duration is not None
        assert 29 <= duration <= 31  # Allow small timing variance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
