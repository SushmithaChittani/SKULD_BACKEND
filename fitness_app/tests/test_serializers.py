import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from ..models import (
    WorkoutPlan, Exercise, WorkoutSession, WorkoutExercise,
    WorkoutMedia, NutritionLog, ProgressPhoto, Post, Comment,
    Like, Challenge, UserChallenge, FollowRequest, Follow
)
from ..serializers import (
    UserRegisterSerializer, UserSerializer, FollowRequestSerializer,
    FollowSerializer, WorkoutPlanSerializer, ExerciseSerializer,
    WorkoutExerciseSerializer, WorkoutMediaSerializer,
    WorkoutSessionSerializer, NutritionLogSerializer,
    ProgressPhotoSerializer, PostSerializer, CommentSerializer,
    LikeSerializer, ChallengeSerializer, UserChallengeSerializer
)

User = get_user_model()

class UserFactory:
    @staticmethod
    def create_user():
        return User.objects.create_user(
            email='test@example.com',
            name='Test User',
            username='testuser',
            password='testpass123'
        )

class UserSerializerTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'username': 'testuser',
            'password': 'testpass123',
            'height': 175.5,
            'weight': 70.2
        }

    def test_user_register_serializer(self):
        serializer = UserRegisterSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_serializer(self):
        user = UserFactory.create_user()
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertEqual(serializer.data['height'], None)  # Not in initial data
        self.assertNotIn('password', serializer.data)

class FollowSerializerTests(TestCase):
    def setUp(self):
        self.user1 = UserFactory.create_user()
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            name='User Two',
            username='user2',
            password='testpass123'
        )
        self.request = type('Request', (), {'user': self.user1})()

    def test_follow_request_serializer(self):
        data = {
            'to_user': self.user2.id,
            'status': 'pending',
            'from_user': self.user1.id  # Added required field
        }
        serializer = FollowRequestSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        follow_request = serializer.save()
        self.assertEqual(follow_request.from_user, self.user1)
        self.assertEqual(follow_request.to_user, self.user2)

    def test_follow_serializer(self):
        follow = Follow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        serializer = FollowSerializer(follow)
        self.assertEqual(serializer.data['follower']['username'], 'testuser')
        self.assertEqual(serializer.data['following']['username'], 'user2')

class WorkoutSerializerTests(TestCase):
    def setUp(self):
        self.user = UserFactory.create_user()
        self.request = type('Request', (), {'user': self.user})()
        self.workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            name='Test Plan',
            difficulty='beginner'
        )
        self.exercise = Exercise.objects.create(
            name='Push Up',
            created_by=self.user
        )
        self.workout_session = WorkoutSession.objects.create(
            user=self.user,
            name='Test Session',
            start_time=timezone.now()
        )

    def test_workout_plan_serializer(self):
        serializer = WorkoutPlanSerializer(self.workout_plan)
        self.assertEqual(serializer.data['name'], 'Test Plan')
        self.assertEqual(serializer.data['difficulty'], 'beginner')

    def test_workout_media_serializer(self):
        test_image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"  # Changed to image instead of video
        )
        data = {
            'workout_session': self.workout_session.id,
            'media_type': 'image',
            'file': test_image,
            'caption': 'Test image',
            'user': self.user.id  # Added required field
        }
        serializer = WorkoutMediaSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        media = serializer.save()
        self.assertEqual(media.media_type, 'image')
        self.assertTrue(media.file.name.startswith('workouts/'))

class NutritionSerializerTests(TestCase):
    def setUp(self):
        self.user = UserFactory.create_user()
        self.request = type('Request', (), {'user': self.user})()

    def test_nutrition_log_serializer(self):
        data = {
            'meal_type': 'breakfast',
            'name': 'Oatmeal',
            'calories': 300,
            'protein': 10,
            'carbs': 50,
            'fats': 5,
            'date': '2023-01-01',
            'time': '08:00:00',
            'user': self.user.id  # Added required field
        }
        serializer = NutritionLogSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        nutrition_log = serializer.save()
        self.assertEqual(nutrition_log.user, self.user)
        self.assertEqual(nutrition_log.name, 'Oatmeal')

class ProgressPhotoSerializerTests(TestCase):
    def setUp(self):
        self.user = UserFactory.create_user()
        self.request = type('Request', (), {'user': self.user})()

    def test_progress_photo_serializer(self):
        test_image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        data = {
            'photo': test_image,
            'weight': 75.5,
            'date': '2023-01-01',
            'user': self.user.id  # Added required field
        }
        serializer = ProgressPhotoSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        progress_photo = serializer.save()
        self.assertEqual(progress_photo.user, self.user)
        self.assertEqual(progress_photo.weight, 75.5)

class SocialSerializerTests(TestCase):
    def setUp(self):
        self.user = UserFactory.create_user()
        self.request = type('Request', (), {'user': self.user})()
        self.post = Post.objects.create(
            user=self.user,
            content='Test post content'
        )

    def test_post_with_image(self):
        test_image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        data = {
            'content': 'Post with image',
            'image': test_image,
            'user': self.user.id  # Added required field
        }
        serializer = PostSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()
        self.assertEqual(post.user, self.user)
        self.assertTrue(post.image.name.startswith('posts/'))

class ChallengeSerializerTests(TestCase):
    def setUp(self):
        self.user = UserFactory.create_user()
        self.request = type('Request', (), {'user': self.user})()

    def test_challenge_serializer(self):
        data = {
            'name': '30-Day Challenge',
            'description': 'Complete 30 workouts in 30 days',
            'start_date': '2023-01-01',
            'end_date': '2023-01-30',
            'target': 30,
            'target_type': 'workouts',
            'created_by': self.user.id  # Added required field
        }
        serializer = ChallengeSerializer(
            data=data,
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        challenge = serializer.save()
        self.assertEqual(challenge.created_by, self.user)
        self.assertEqual(challenge.target, 30)

    def test_challenge_date_validation(self):
        data = {
            'name': 'Invalid Challenge',
            'description': 'End date before start date',
            'start_date': '2023-01-30',
            'end_date': '2023-01-01',
            'target': 10,
            'target_type': 'workouts',
            'created_by': self.user.id  # Added required field
        }
        serializer = ChallengeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)