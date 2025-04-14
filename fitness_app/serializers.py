from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from .utils.file_handling import validate_image_extension, validate_video_extension, validate_image_size,validate_video_size

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['name'] = user.name
        token['username'] = user.username
        token['email'] = user.email
        
        return token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'username', 'bio', 'date_of_birth', 
                 'gender', 'height', 'weight', 'profile_picture', 'fitness_goals',
                 'current_streak', 'longest_streak', 'total_points']
        extra_kwargs = {
            'email': {'read_only': True},
            'username': {'read_only': True},
        }

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'username', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class FollowRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    
    class Meta:
        model = FollowRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']

class WorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'user', 'name', 'description', 'difficulty', 'is_public', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'muscle_group', 'equipment', 
                 'is_public', 'created_by', 'demonstration_video']
        read_only_fields = ['created_by']

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
        write_only=True
    )
    
    class Meta:
        model = WorkoutExercise
        fields = ['id', 'workout_session', 'exercise', 'exercise_id', 'sets', 'reps', 
                 'weight', 'duration', 'rest_time', 'notes', 'order']
        read_only_fields = ['workout_session']

class WorkoutMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutMedia
        fields = ['id', 'workout_session', 'media_type', 'file', 'uploaded_at', 'caption']
        read_only_fields = ['workout_session', 'uploaded_at']
    
    def validate_file(self, value):
        if self.initial_data.get('media_type') == 'image':
            validate_image_extension(value)
        elif self.initial_data.get('media_type') == 'video':
            validate_video_extension(value)
        return value

class WorkoutSessionSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, read_only=True)
    media_files = WorkoutMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkoutSession
        fields = ['id', 'user', 'workout_plan', 'name', 'notes', 'start_time', 'end_time',
                 'calories_burned', 'points_earned', 'is_completed', 'exercises', 'media_files']
        read_only_fields = ['user', 'points_earned', 'is_completed']

class DailyActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyActivity
        fields = ['id', 'user', 'date', 'steps', 'distance', 'calories_burned', 'active_minutes']
        read_only_fields = ['user']

class NutritionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionLog
        fields = ['id', 'user', 'meal_type', 'name', 'calories', 'protein', 'carbs', 
                 'fats', 'date', 'time', 'notes', 'meal_image']
        read_only_fields = ['user']
    
    def validate_meal_image(self, value):
        if value:
            validate_image_extension(value)
        return value

class ProgressPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressPhoto
        fields = ['id', 'user', 'photo', 'weight', 'body_fat_percentage', 
                 'muscle_mass', 'date', 'notes']
        read_only_fields = ['user']
    
    def validate_photo(self, value):
        validate_image_extension(value)
        return value

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'created_at', 'updated_at', 
                 'likes_count', 'comments_count']
        read_only_fields = ['user', 'created_at', 'updated_at', 'likes_count', 'comments_count']
    
    def validate_image(self, value):
        if value:
            validate_image_extension(value)
        return value

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class ChallengeSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Challenge
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'target', 
                 'target_type', 'created_by', 'participants', 'is_active', 'image', 'is_ongoing']
        read_only_fields = ['created_by', 'participants', 'is_ongoing']
    
    def validate_image(self, value):
        if value:
            validate_image_extension(value)
        return value
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

class UserChallengeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    challenge = ChallengeSerializer(read_only=True)
    
    class Meta:
        model = UserChallenge
        fields = ['id', 'user', 'challenge', 'progress', 'completed', 'completed_at']
        read_only_fields = ['user', 'challenge', 'progress', 'completed', 'completed_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'message', 'is_read', 'created_at', 'related_id']
        read_only_fields = ['created_at']

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']
    
    def validate_profile_picture(self, value):
        validate_image_extension(value)
        validate_image_size(value)  # From utils/validators.py
        return value

class WorkoutMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutMedia
        fields = ['id', 'workout_session', 'media_type', 'file', 'uploaded_at', 'caption']
        read_only_fields = ['workout_session', 'uploaded_at']
    
    def validate(self, data):
        media_type = data.get('media_type')
        file = data.get('file')
        
        if media_type == 'image':
            validate_image_extension(file)
            validate_image_size(file)
        elif media_type == 'video':
            validate_video_extension(file)
            validate_video_size(file)
        
        return data

class ProgressPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressPhoto
        fields = ['id', 'user', 'photo', 'weight', 'body_fat_percentage', 
                 'muscle_mass', 'date', 'notes']
        read_only_fields = ['user']
    
    def validate_photo(self, value):
        validate_image_extension(value)
        validate_image_size(value)
        return value

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['image']
    
    def validate_image(self, value):
        validate_image_extension(value)
        validate_image_size(value)
        return value

class MealImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionLog
        fields = ['meal_image']
    
    def validate_meal_image(self, value):
        validate_image_extension(value)
        validate_image_size(value)
        return value
    
class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    name = serializers.CharField(source='user.name')
    profile_picture = serializers.ImageField(source='user.profile_picture')
    rank = serializers.SerializerMethodField()

    class Meta:
        model = UserScore
        fields = ['rank', 'username', 'name', 'profile_picture', 'points', 'workouts_completed']
    
    def get_rank(self, obj):
        # This assumes queryset is already ordered by points
        queryset = self.context.get('queryset')
        if queryset:
            return list(queryset).index(obj) + 1
        return None