from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import WorkoutPlan, WorkoutSession, WorkoutExercise, WorkoutMedia
from django.db import models
from ..models import Exercise
from ..serializers import ExerciseSerializer
from rest_framework.permissions import IsAuthenticated
from ..serializers import (
    WorkoutPlanSerializer, WorkoutSessionSerializer, 
    WorkoutExerciseSerializer, WorkoutMediaSerializer
)

class WorkoutPlanListView(generics.ListCreateAPIView):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutPlan.objects.filter(
            models.Q(user=self.request.user) | 
            models.Q(is_public=True)
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WorkoutPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutPlan.objects.filter(
            models.Q(user=self.request.user) | 
            models.Q(is_public=True)
        )

class WorkoutSessionListView(generics.ListCreateAPIView):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user).order_by('-start_time')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WorkoutSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkoutSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

class WorkoutExerciseCreateView(generics.CreateAPIView):
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        workout_session = get_object_or_404(
            WorkoutSession,
            id=self.kwargs['workout_id'],
            user=self.request.user
        )
        serializer.save(workout_session=workout_session)

class WorkoutExerciseUpdateView(generics.UpdateAPIView):
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutExercise.objects.filter(
            workout_session__user=self.request.user
        )

class WorkoutExerciseDestroyView(generics.DestroyAPIView):
    serializer_class = WorkoutExerciseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutExercise.objects.filter(
            workout_session__user=self.request.user
        )

class WorkoutMediaCreateView(generics.CreateAPIView):
    serializer_class = WorkoutMediaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        workout_session = get_object_or_404(
            WorkoutSession,
            id=self.kwargs['workout_id'],
            user=self.request.user
        )
        serializer.save(workout_session=workout_session)

class WorkoutMediaDestroyView(generics.DestroyAPIView):
    serializer_class = WorkoutMediaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutMedia.objects.filter(
            workout_session__user=self.request.user
        )
    
class ExerciseCreateView(generics.CreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ExerciseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]