from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from fitness_app.views.workouts import *
# Authentication
from fitness_app.views.auth import (
    UserRegisterView, CustomTokenObtainPairView, UserProfileView
)

# Users & Follow System
from fitness_app.views.users import (
    UserListView, UserDetailView,
    FollowRequestCreateView, FollowRequestListView, FollowRequestUpdateView,
    FollowListView, FollowDestroyView
)

# Workouts
from fitness_app.views.workouts import (
    WorkoutPlanListView, WorkoutPlanDetailView,
    WorkoutSessionListView, WorkoutSessionDetailView,
    WorkoutExerciseCreateView, WorkoutExerciseUpdateView, WorkoutExerciseDestroyView
    # ExerciseListCreateView,WorkoutMediaCreateView, WorkoutMediaDestroyView
)

# Nutrition
from fitness_app.views.nutrition import (
    NutritionLogListView, NutritionLogDetailView, NutritionLogTodayView
)

# Social
from fitness_app.views.social import (
    PostListView, PostDetailView,
    LikeCreateView, LikeDestroyView,
    CommentListView, CommentDetailView
)

# Challenges
from fitness_app.views.challenges import (
    ChallengeListView, ChallengeDetailView, ChallengeJoinView,
    UserChallengeListView, UserChallengeDetailView
)

# Media
from fitness_app.views.media import (
    ProfilePictureUploadView,
    WorkoutMediaUploadView, WorkoutMediaDeleteView,
    ProgressPhotoUploadView, ProgressPhotoDeleteView,
    PostImageUploadView, MealImageUploadView,
    MediaStorageView
)

# Leaderboard
from fitness_app.views.leaderboard import (
    GlobalLeaderboardView, ChallengeLeaderboardView
)

urlpatterns = [
    # ==================== Authentication ====================
    path('auth/register/', UserRegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # ==================== User Management ====================
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user-detail'),

    # ==================== Follow System ====================
    path('users/<str:username>/follow-request/', FollowRequestCreateView.as_view(), name='follow-request-create'),
    path('follow-requests/', FollowRequestListView.as_view(), name='follow-request-list'),
    path('follow-requests/<int:id>/', FollowRequestUpdateView.as_view(), name='follow-request-update'),
    path('users/<str:username>/follows/', FollowListView.as_view(), name='follow-list'),
    path('users/<str:username>/unfollow/', FollowDestroyView.as_view(), name='follow-destroy'),

    # ==================== Workouts ====================
    path('workouts/plans/', WorkoutPlanListView.as_view(), name='workout-plan-list'),
    path('workouts/plans/<int:pk>/', WorkoutPlanDetailView.as_view(), name='workout-plan-detail'),
    path('workouts/sessions/', WorkoutSessionListView.as_view(), name='workout-session-list'),
    path('workouts/sessions/<int:pk>/', WorkoutSessionDetailView.as_view(), name='workout-session-detail'),
    path('workouts/sessions/<int:workout_id>/exercises/', WorkoutExerciseCreateView.as_view(), name='workout-exercise-create'),
    path('workouts/exercises/<int:pk>/', WorkoutExerciseUpdateView.as_view(), name='workout-exercise-update'),
    path('workouts/exercises/<int:pk>/delete/', WorkoutExerciseDestroyView.as_view(), name='workout-exercise-delete'),
  
    # # Exercises CRUD
    # path('workouts/exercises/', ExerciseListCreateView.as_view(), name='exercise-list-create'),
    # path('workouts/exercises/<int:pk>/', ExerciseRetrieveUpdateDestroyView.as_view(), name='exercise-detail-update-delete'),

    # ==================== Workout Media ====================
    path('workouts/sessions/<int:workout_id>/media/', WorkoutMediaUploadView.as_view(), name='workout-media-upload'),
    path('workouts/media/<int:pk>/delete/', WorkoutMediaDeleteView.as_view(), name='workout-media-delete'),

    # ==================== Nutrition ====================
    path('nutrition/logs/', NutritionLogListView.as_view(), name='nutrition-log-list'),
    path('nutrition/logs/<int:pk>/', NutritionLogDetailView.as_view(), name='nutrition-log-detail'),
    path('nutrition/logs/today/', NutritionLogTodayView.as_view(), name='nutrition-log-today'),

    # ==================== Social ====================
    path('social/posts/', PostListView.as_view(), name='post-list'),
    path('social/posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('social/posts/<int:post_id>/like/', LikeCreateView.as_view(), name='like-create'),
    path('social/posts/<int:post_id>/unlike/', LikeDestroyView.as_view(), name='like-destroy'),
    path('social/posts/<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'),
    path('social/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    # ==================== Challenges ====================
    path('challenges/', ChallengeListView.as_view(), name='challenge-list'),
    path('challenges/<int:pk>/', ChallengeDetailView.as_view(), name='challenge-detail'),
    path('challenges/<int:pk>/join/', ChallengeJoinView.as_view(), name='challenge-join'),
    path('challenges/my-challenges/', UserChallengeListView.as_view(), name='user-challenge-list'),
    path('challenges/my-challenges/<int:pk>/', UserChallengeDetailView.as_view(), name='user-challenge-detail'),

    # ==================== Media ====================
    path('media/profile/picture/', ProfilePictureUploadView.as_view(), name='profile-picture-upload'),
    path('media/progress/photos/', ProgressPhotoUploadView.as_view(), name='progress-photo-upload'),
    path('media/progress/photos/<int:pk>/delete/', ProgressPhotoDeleteView.as_view(), name='progress-photo-delete'),
    path('media/posts/<int:pk>/image/', PostImageUploadView.as_view(), name='post-image-upload'),
    path('media/nutrition-logs/<int:pk>/meal-image/', MealImageUploadView.as_view(), name='meal-image-upload'),
    path('media/storage/', MediaStorageView.as_view(), name='media-storage'),

    # ==================== Leaderboard ====================
    path('leaderboard/', GlobalLeaderboardView.as_view(), name='global-leaderboard'),
    path('challenges/<int:challenge_id>/leaderboard/', ChallengeLeaderboardView.as_view(), name='challenge-leaderboard'),

    # ==================== (Optional future) Activity Tracking ====================
    # path('activity/daily/', DailyActivityListView.as_view(), name='daily-activity-list'),
    # path('activity/daily/<int:pk>/', DailyActivityDetailView.as_view(), name='daily-activity-detail'),
]
