from django.utils import timezone
from datetime import timedelta

def update_streak(user):
    """Update user's streak based on last activity"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    if user.last_activity:
        last_activity_date = user.last_activity.date()
        if last_activity_date == today:
            return  # Already updated today
        elif last_activity_date == yesterday:
            user.current_streak += 1
        else:
            user.current_streak = 1
        
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    else:
        user.current_streak = 1
    
    user.last_activity = timezone.now()
    user.save()