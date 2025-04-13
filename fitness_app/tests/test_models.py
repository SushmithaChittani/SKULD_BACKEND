from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from ..models import (
    FollowRequest, Follow, WorkoutPlan, Exercise, WorkoutSession,
    WorkoutExercise, WorkoutMedia, DailyActivity, NutritionLog,
    ProgressPhoto, Post, Like, Comment, Challenge, UserChallenge,
    Notification
)

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            username='testuser',
            password='testpass123'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
    
    def test_update_streak(self):
        # First activity
        self.user.update_streak()
        self.assertEqual(self.user.current_streak, 1)
        
        # Activity on same day shouldn't increase streak
        self.user.update_streak()
        self.assertEqual(self.user.current_streak, 1)
        
        # Simulate activity next day
        self.user.last_activity = self.user.last_activity - timedelta(days=1)
        self.user.update_streak()
        self.assertEqual(self.user.current_streak, 2)
        
        # Simulate broken streak
        self.user.last_activity = self.user.last_activity - timedelta(days=2)
        self.user.update_streak()
        self.assertEqual(self.user.current_streak, 1)
    
    def test_add_points(self):
        self.user.add_points(100)
        self.assertEqual(self.user.total_points, 100)
        self.user.add_points(50)
        self.assertEqual(self.user.total_points, 150)

class FollowRequestModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            name='User One',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            name='User Two',
            username='user2',
            password='testpass123'
        )
        self.follow_request = FollowRequest.objects.create(
            from_user=self.user1,
            to_user=self.user2
        )
    
    def test_follow_request_creation(self):
        self.assertEqual(self.follow_request.status, 'pending')
        self.assertEqual(self.follow_request.from_user, self.user1)
        self.assertEqual(self.follow_request.to_user, self.user2)
    
    def test_accept_follow_request(self):
        self.follow_request.accept()
        self.assertEqual(self.follow_request.status, 'accepted')
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())
        self.assertEqual(self.user1.following_count, 1)
        self.assertEqual(self.user2.followers_count, 1)
    
    def test_reject_follow_request(self):
        self.follow_request.reject()
        self.assertEqual(self.follow_request.status, 'rejected')
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

# Similar test classes would be created for all other models