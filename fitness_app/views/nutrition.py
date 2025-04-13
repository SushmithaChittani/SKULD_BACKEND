from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from ..models import NutritionLog
from ..serializers import NutritionLogSerializer
from django.db import models
from datetime import date

class NutritionLogListView(generics.ListCreateAPIView):
    serializer_class = NutritionLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['meal_type', 'date']
    search_fields = ['name']
    
    def get_queryset(self):
        queryset = NutritionLog.objects.filter(user=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(date__gte=start_date)
        elif end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date', '-time')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NutritionLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NutritionLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NutritionLog.objects.filter(user=self.request.user)

class NutritionLogTodayView(generics.ListAPIView):
    serializer_class = NutritionLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        today = date.today()
        return NutritionLog.objects.filter(
            user=self.request.user,
            date=today
        ).order_by('time')