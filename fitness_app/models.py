from django.db import models

# Create your models here.
import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from .managers import CustomUserManager
from .utils.file_handling import validate_image_extension, validate_video_extension


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<type>/<filename>
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"user_{instance.user.id}/{instance.__class__.__name__.lower()}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Profile fields
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Prefer not to say')
    ], blank=True, null=True)
    height = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])  # in cm
    weight = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])  # in kg
    fitness_goals = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[validate_image_extension]
    )
    
    # Activity tracking
    last_activity = models.DateTimeField(blank=True, null=True)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']
    
    def __str__(self):
        return self.email
    
    def update_streak(self):
        """Update user's streak based on last activity"""
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        
        if self.last_activity:
            last_activity_date = self.last_activity.date()
            if last_activity_date == today:
                return  # Already updated today
            elif last_activity_date == yesterday:
                self.current_streak += 1
            else:
                self.current_streak = 1
            
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 1
        
        self.last_activity = timezone.now()
        self.save()
    
    def add_points(self, points):
        """Add points to user's total"""
        self.total_points += points
        self.save()


class FollowRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_follow_requests',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_follow_requests',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def accept(self):
        """Accept the follow request and create a follow relationship"""
        self.status = self.ACCEPTED
        self.save()
        Follow.objects.get_or_create(follower=self.from_user, following=self.to_user)
        
        # Update counts
        self.from_user.following_count = Follow.objects.filter(follower=self.from_user).count()
        self.from_user.save()
        self.to_user.followers_count = Follow.objects.filter(following=self.to_user).count()
        self.to_user.save()
    
    def reject(self):
        """Reject the follow request"""
        self.status = self.REJECTED
        self.save()


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']


class WorkoutPlan(models.Model):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    DIFFICULTY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='workout_plans',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    muscle_group = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.CharField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_exercises',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    demonstration_video = models.FileField(
        upload_to='exercise_videos/',
        blank=True,
        null=True,
        validators=[validate_video_extension]
    )
    
    def __str__(self):
        return self.name


class WorkoutSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='workout_sessions',
        on_delete=models.CASCADE
    )
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        related_name='sessions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    calories_burned = models.FloatField(default=0, validators=[MinValueValidator(0)])
    points_earned = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_completed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds() / 60  # in minutes
            self.points_earned = int(duration * settings.WORKOUT_POINTS_PER_MINUTE)
            self.is_completed = True
            self.user.update_streak()
            self.user.add_points(self.points_earned)
            
            # Streak bonus
            if self.user.current_streak % 7 == 0:  # Weekly streak bonus
                bonus = settings.STREAK_BONUS_POINTS * (self.user.current_streak // 7)
                self.user.add_points(bonus)
                self.points_earned += bonus
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s workout on {self.start_time.date()}"


class WorkoutExercise(models.Model):
    workout_session = models.ForeignKey(
        WorkoutSession,
        related_name='exercises',
        on_delete=models.CASCADE
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    reps = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])
    weight = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])  # in kg
    duration = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1)])  # in seconds
    rest_time = models.PositiveIntegerField(default=60, validators=[MinValueValidator(1)])  # in seconds
    notes = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.exercise.name} in {self.workout_session}"


class WorkoutMedia(models.Model):
    IMAGE = 'image'
    VIDEO = 'video'
    MEDIA_TYPES = [
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
    ]
    
    workout_session = models.ForeignKey(
        WorkoutSession,
        related_name='media_files',
        on_delete=models.CASCADE
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(
        upload_to=user_directory_path,
        validators=[validate_image_extension, validate_video_extension]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    
    def clean(self):
        if self.media_type == self.IMAGE:
            validate_image_extension(self.file)
        elif self.media_type == self.VIDEO:
            validate_video_extension(self.file)
    
    def __str__(self):
        return f"{self.media_type} for {self.workout_session}"


class DailyActivity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='daily_activities',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    steps = models.PositiveIntegerField(default=0)
    distance = models.FloatField(default=0, validators=[MinValueValidator(0)])  # in km
    calories_burned = models.FloatField(default=0, validators=[MinValueValidator(0)])
    active_minutes = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        verbose_name_plural = 'Daily Activities'
    
    def __str__(self):
        return f"{self.user.username}'s activity on {self.date}"


class NutritionLog(models.Model):
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    SNACK = 'snack'
    MEAL_TYPES = [
        (BREAKFAST, 'Breakfast'),
        (LUNCH, 'Lunch'),
        (DINNER, 'Dinner'),
        (SNACK, 'Snack'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='nutrition_logs',
        on_delete=models.CASCADE
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    name = models.CharField(max_length=255)
    calories = models.FloatField(validators=[MinValueValidator(0)])
    protein = models.FloatField(validators=[MinValueValidator(0)])
    carbs = models.FloatField(validators=[MinValueValidator(0)])
    fats = models.FloatField(validators=[MinValueValidator(0)])
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    meal_image = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
        validators=[validate_image_extension]
    )
    
    class Meta:
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.meal_type}: {self.name} ({self.date})"


class ProgressPhoto(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='progress_photos',
        on_delete=models.CASCADE
    )
    photo = models.ImageField(
        upload_to=user_directory_path,
        validators=[validate_image_extension]
    )
    weight = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    body_fat_percentage = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    muscle_mass = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0)])
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username}'s progress on {self.date}"


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='posts',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    image = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
        validators=[validate_image_extension]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.user.username}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='likes',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='likes',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post.likes_count = self.post.likes.count()
        self.post.save()
    
    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)
        post.likes_count = post.likes.count()
        post.save()


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post.comments_count = self.post.comments.count()
        self.post.save()
    
    def delete(self, *args, **kwargs):
        post = self.post
        super().delete(*args, **kwargs)
        post.comments_count = post.comments.count()
        post.save()
    
    def __str__(self):
        return f"Comment by {self.user.username}"


class Challenge(models.Model):
    WORKOUTS = 'workouts'
    STEPS = 'steps'
    DISTANCE = 'distance'
    POINTS = 'points'
    TARGET_TYPES = [
        (WORKOUTS, 'Workouts Completed'),
        (STEPS, 'Steps'),
        (DISTANCE, 'Distance (km)'),
        (POINTS, 'Points Earned'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    target = models.PositiveIntegerField()
    target_type = models.CharField(max_length=50, choices=TARGET_TYPES)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_challenges',
        on_delete=models.CASCADE
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='challenges',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to='challenge_images/',
        blank=True,
        null=True,
        validators=[validate_image_extension]
    )
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    @property
    def is_ongoing(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class UserChallenge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_challenges',
        on_delete=models.CASCADE
    )
    challenge = models.ForeignKey(
        Challenge,
        related_name='user_challenges',
        on_delete=models.CASCADE
    )
    progress = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def update_progress(self):
        """Update progress based on challenge type"""
        if self.challenge.target_type == Challenge.WORKOUTS:
            self.progress = self.user.workout_sessions.filter(
                is_completed=True,
                start_time__date__range=[self.challenge.start_date, self.challenge.end_date]
            ).count()
        elif self.challenge.target_type == Challenge.STEPS:
            self.progress = self.user.daily_activities.filter(
                date__range=[self.challenge.start_date, self.challenge.end_date]
            ).aggregate(models.Sum('steps'))['steps__sum'] or 0
        elif self.challenge.target_type == Challenge.DISTANCE:
            self.progress = self.user.daily_activities.filter(
                date__range=[self.challenge.start_date, self.challenge.end_date]
            ).aggregate(models.Sum('distance'))['distance__sum'] or 0
        elif self.challenge.target_type == Challenge.POINTS:
            self.progress = self.user.workout_sessions.filter(
                is_completed=True,
                start_time__date__range=[self.challenge.start_date, self.challenge.end_date]
            ).aggregate(models.Sum('points_earned'))['points_earned__sum'] or 0
        
        # Check if challenge is completed
        if self.progress >= self.challenge.target and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.user.add_points(settings.CHALLENGE_COMPLETION_POINTS)
        
        self.save()
    
    def __str__(self):
        return f"{self.user.username}'s progress in {self.challenge.name}"


class Notification(models.Model):
    FOLLOW = 'follow'
    LIKE = 'like'
    COMMENT = 'comment'
    CHALLENGE = 'challenge'
    WORKOUT = 'workout'
    NOTIFICATION_TYPES = [
        (FOLLOW, 'New Follow'),
        (LIKE, 'New Like'),
        (COMMENT, 'New Comment'),
        (CHALLENGE, 'Challenge Update'),
        (WORKOUT, 'Workout Reminder'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_id = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.user.username}"