from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import (
    FollowRequest, Follow, WorkoutPlan, Exercise, WorkoutSession,
    WorkoutExercise, WorkoutMedia, DailyActivity, NutritionLog,
    ProgressPhoto, Post, Like, Comment, Challenge, UserChallenge,
    Notification
)

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        
        self.user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
    
    def test_user_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_profile(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

class WorkoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            name='Test Plan',
            difficulty='beginner'
        )
        
        self.workout_session = WorkoutSession.objects.create(
            user=self.user,
            name='Test Session',
            start_time='2023-01-01T10:00:00Z'
        )
        
        self.exercise = Exercise.objects.create(
            name='Test Exercise',
            created_by=self.user
        )
        
        self.workout_exercise = WorkoutExercise.objects.create(
            workout_session=self.workout_session,
            exercise=self.exercise
        )
    
    def test_create_workout_plan(self):
        url = reverse('workout-plan-list')
        data = {
            'name': 'New Plan',
            'difficulty': 'intermediate',
            'is_public': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutPlan.objects.count(), 2)
    
    def test_create_workout_session(self):
        url = reverse('workout-session-list')
        data = {
            'name': 'New Session',
            'start_time': '2023-01-02T10:00:00Z',
            'workout_plan': self.workout_plan.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutSession.objects.count(), 2)
    
    # Similar tests for other workout-related endpoints

# Similar test classes would be created for all other view categories