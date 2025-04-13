from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from ..models import FollowRequest, Follow
from ..serializers import UserSerializer, FollowRequestSerializer, FollowSerializer
from django.db import models
from rest_framework.exceptions import ValidationError

User = get_user_model()

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.exclude(id=self.request.user.id)
        
        # Search by username or name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) | 
                models.Q(name__icontains=search)
            )
        
        return queryset

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'

class FollowRequestCreateView(generics.CreateAPIView):
    queryset = FollowRequest.objects.all()
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        to_user = get_object_or_404(User, username=self.kwargs['username'])
        if FollowRequest.objects.filter(from_user=self.request.user, to_user=to_user).exists():
            #raise serializers.ValidationError("Follow request already sent.")
            raise ValidationError("Follow request already sent.")
        serializer.save(from_user=self.request.user, to_user=to_user)

class FollowRequestListView(generics.ListAPIView):
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FollowRequest.objects.filter(to_user=self.request.user, status='pending')

class FollowRequestUpdateView(generics.UpdateAPIView):
    queryset = FollowRequest.objects.all()
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.to_user != self.request.user:
            raise PermissionDenied("You can't update this follow request.")
        
        status = serializer.validated_data.get('status')
        if status == 'accepted':
            instance.accept()
        elif status == 'rejected':
            instance.reject()
        else:
            serializer.save()

class FollowListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.query_params.get('type') == 'followers':
            return Follow.objects.filter(following=user)
        return Follow.objects.filter(follower=user)

class FollowDestroyView(generics.DestroyAPIView):
    queryset = Follow.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user_to_unfollow = get_object_or_404(User, username=self.kwargs['username'])
        return get_object_or_404(
            Follow,
            follower=self.request.user,
            following=user_to_unfollow
        )
    
    def perform_destroy(self, instance):
        # Update follower/following counts
        follower = instance.follower
        following = instance.following
        
        super().perform_destroy(instance)
        
        follower.following_count = Follow.objects.filter(follower=follower).count()
        follower.save()
        
        following.followers_count = Follow.objects.filter(following=following).count()
        following.save()