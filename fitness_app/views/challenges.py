from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Challenge, UserChallenge
from ..serializers import ChallengeSerializer, UserChallengeSerializer
from django.db import models

class ChallengeListView(generics.ListCreateAPIView):
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Challenge.objects.filter(is_active=True)
        
        # Filter by participation status
        participation = self.request.query_params.get('participation', None)
        if participation == 'joined':
            queryset = queryset.filter(participants=self.request.user)
        elif participation == 'available':
            queryset = queryset.exclude(participants=self.request.user)
        
        return queryset.order_by('-start_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ChallengeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Challenge.objects.filter(
            models.Q(created_by=self.request.user) | 
            models.Q(is_active=True)
        )

class ChallengeJoinView(generics.CreateAPIView):
    serializer_class = UserChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        challenge = get_object_or_404(Challenge, id=self.kwargs['pk'], is_active=True)
        
        if challenge.participants.filter(id=self.request.user.id).exists():
            return Response(
                {'detail': 'You have already joined this challenge.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        challenge.participants.add(self.request.user)
        user_challenge = UserChallenge.objects.create(
            user=self.request.user,
            challenge=challenge
        )
        
        serializer = self.get_serializer(user_challenge)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserChallengeListView(generics.ListAPIView):
    serializer_class = UserChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserChallenge.objects.filter(user=self.request.user).order_by('-challenge__start_date')

class UserChallengeDetailView(generics.RetrieveAPIView):
    serializer_class = UserChallengeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserChallenge.objects.filter(user=self.request.user)