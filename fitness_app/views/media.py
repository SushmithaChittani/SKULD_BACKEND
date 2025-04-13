import os
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from ..models import User, WorkoutMedia, ProgressPhoto, Post, NutritionLog
from ..serializers import (
    ProfilePictureSerializer,
    WorkoutMediaSerializer,
    ProgressPhotoSerializer,
    PostImageSerializer,
    MealImageSerializer
)
from ..utils.file_handling import (
    validate_image_extension,
    validate_video_extension,
    delete_old_file
)

class ProfilePictureUploadView(generics.UpdateAPIView):
    serializer_class = ProfilePictureSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        
        if serializer.is_valid():
            # Delete old profile picture if exists
            if user.profile_picture:
                delete_old_file(user.profile_picture.path)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkoutMediaUploadView(generics.CreateAPIView):
    serializer_class = WorkoutMediaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        workout_session = get_object_or_404(
            self.request.user.workout_sessions,
            id=self.kwargs['workout_id']
        )
        
        # Validate file based on media type
        media_type = self.request.data.get('media_type')
        file = self.request.data.get('file')
        
        if media_type == 'image':
            validate_image_extension(file)
        elif media_type == 'video':
            validate_video_extension(file)
        
        serializer.save(workout_session=workout_session)

class WorkoutMediaDeleteView(generics.DestroyAPIView):
    queryset = WorkoutMedia.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(workout_session__user=self.request.user)

    def perform_destroy(self, instance):
        if instance.file:
            delete_old_file(instance.file.path)
        instance.delete()

class ProgressPhotoUploadView(generics.CreateAPIView):
    serializer_class = ProgressPhotoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        validate_image_extension(self.request.data.get('photo'))
        serializer.save(user=self.request.user)

class ProgressPhotoDeleteView(generics.DestroyAPIView):
    queryset = ProgressPhoto.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.photo:
            delete_old_file(instance.photo.path)
        instance.delete()

class PostImageUploadView(generics.UpdateAPIView):
    serializer_class = PostImageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)
        
        if serializer.is_valid():
            # Delete old image if exists
            if post.image:
                delete_old_file(post.image.path)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MealImageUploadView(generics.UpdateAPIView):
    serializer_class = MealImageSerializer
    permission_classes = [IsAuthenticated]
    queryset = NutritionLog.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        nutrition_log = self.get_object()
        serializer = self.get_serializer(nutrition_log, data=request.data)
        
        if serializer.is_valid():
            # Delete old image if exists
            if nutrition_log.meal_image:
                delete_old_file(nutrition_log.meal_image.path)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MediaStorageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Check media storage usage"""
        user = request.user
        media_path = os.path.join(settings.MEDIA_ROOT, f'user_{user.id}')
        
        if not os.path.exists(media_path):
            return Response({'usage': 0, 'limit': settings.MAX_MEDIA_STORAGE})
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(media_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        
        return Response({
            'usage': total_size,
            'limit': settings.MAX_MEDIA_STORAGE,
            'unit': 'bytes'
        })