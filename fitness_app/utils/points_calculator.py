from django.conf import settings

def calculate_workout_points(duration_minutes):
    """Calculate points earned for a workout based on duration"""
    return int(duration_minutes * settings.WORKOUT_POINTS_PER_MINUTE)

def calculate_streak_bonus(current_streak):
    """Calculate streak bonus points"""
    if current_streak % 7 == 0:  # Weekly streak bonus
        return settings.STREAK_BONUS_POINTS * (current_streak // 7)
    return 0