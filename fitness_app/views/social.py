from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Post, Like, Comment
from django.db import models
from ..serializers import PostSerializer, LikeSerializer, CommentSerializer
from rest_framework.exceptions import ValidationError

class PostListView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get posts from users the current user follows plus their own posts
        following_users = [follow.following for follow in self.request.user.following.all()]
        following_users.append(self.request.user)
        return Post.objects.filter(user__in=following_users).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if Like.objects.filter(user=self.request.user, post=post).exists():
           #raise serializers.ValidationError("You have already liked this post.")
            raise ValidationError("You have already liked this post.")
        serializer.save(user=self.request.user, post=post)

class LikeDestroyView(generics.DestroyAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return get_object_or_404(
            Like,
            user=self.request.user,
            post=post
        )

class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(post__id=self.kwargs['post_id']).order_by('created_at')
    
    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(user=self.request.user, post=post)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)