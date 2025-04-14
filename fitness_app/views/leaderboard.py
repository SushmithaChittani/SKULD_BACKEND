from django.db.models import F
from rest_framework import generics
from ..models import UserScore
from ..serializers import LeaderboardSerializer
from rest_framework.response import Response

class GlobalLeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    
    def get_queryset(self):
        return UserScore.objects.select_related('user').order_by('-points')[:100]
    
    def get(self, request):
        leaderboard = UserScore.objects.order_by('-points')[:50]
        data = [
            {
                "user": user_score.user.username,
                "points": user_score.points,
                "workouts_completed": user_score.workouts_completed
            }
            for user_score in leaderboard
        ]
        return Response(data)

class ChallengeLeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    
    def get_queryset(self):
        challenge_id = self.kwargs['challenge_id']
        return UserScore.objects.filter(
            user__user_challenges__challenge_id=challenge_id
        ).select_related('user').order_by('-points')[:50]