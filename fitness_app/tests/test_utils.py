from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from ..utils.file_handling import validate_image_extension, validate_video_extension
from ..utils.points_calculator import calculate_workout_points, calculate_streak_bonus
from ..utils.streak_manager import update_streak
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class FileHandlingTests(TestCase):
    def test_validate_image_extension(self):
        valid_image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        validate_image_extension(valid_image)  # Should not raise
        
        invalid_image = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validate_image_extension(invalid_image)
    
    def test_validate_video_extension(self):
        valid_video = SimpleUploadedFile("test.mp4", b"file_content", content_type="video/mp4")
        validate_video_extension(valid_video)  # Should not raise
        
        invalid_video = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validate_video_extension(invalid_video)

class PointsCalculatorTests(TestCase):
    def test_calculate_workout_points(self):
        self.assertEqual(calculate_workout_points(30), 60)  # 30 mins * 2 points/min
    
    def test_calculate_streak_bonus(self):
        self.assertEqual(calculate_streak_bonus(7), 50)  # 1 week streak
        self.assertEqual(calculate_streak_bonus(14), 100)  # 2 weeks streak
        self.assertEqual(calculate_streak_bonus(3), 0)  # No bonus

class StreakManagerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            username='testuser',
            password='testpass123'
        )
    
    def test_update_streak(self):
        # First activity
        update_streak(self.user)
        self.assertEqual(self.user.current_streak, 1)
        
        # Activity on same day shouldn't increase streak
        update_streak(self.user)
        self.assertEqual(self.user.current_streak, 1)
        
        # Simulate activity next day
        self.user.last_activity = timezone.now() - timedelta(days=1)
        self.user.save()
        update_streak(self.user)
        self.assertEqual(self.user.current_streak, 2)
        
        # Simulate broken streak
        self.user.last_activity = timezone.now() - timedelta(days=2)
        self.user.save()
        update_streak(self.user)
        self.assertEqual(self.user.current_streak, 1)