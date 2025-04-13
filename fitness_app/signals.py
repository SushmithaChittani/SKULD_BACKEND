from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
import os
from .models import *

@receiver(pre_delete, sender=User)
def delete_user_files(sender, instance, **kwargs):
    """Delete user's media files when user is deleted"""
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)

@receiver(pre_delete, sender=WorkoutMedia)
def delete_workout_media_files(sender, instance, **kwargs):
    """Delete workout media files when record is deleted"""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(pre_delete, sender=Exercise)
def delete_exercise_video(sender, instance, **kwargs):
    """Delete exercise video when record is deleted"""
    if instance.demonstration_video:
        if os.path.isfile(instance.demonstration_video.path):
            os.remove(instance.demonstration_video.path)

@receiver(pre_delete, sender=NutritionLog)
def delete_meal_image(sender, instance, **kwargs):
    """Delete meal image when record is deleted"""
    if instance.meal_image:
        if os.path.isfile(instance.meal_image.path):
            os.remove(instance.meal_image.path)

@receiver(pre_delete, sender=ProgressPhoto)
def delete_progress_photo(sender, instance, **kwargs):
    """Delete progress photo when record is deleted"""
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)

@receiver(pre_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    """Delete post image when record is deleted"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(pre_delete, sender=Challenge)
def delete_challenge_image(sender, instance, **kwargs):
    """Delete challenge image when record is deleted"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(post_save, sender=WorkoutSession)
def update_user_challenges(sender, instance, created, **kwargs):
    """Update user challenges when a workout is completed"""
    if instance.is_completed:
        # Get all active challenges for this user
        challenges = instance.user.challenges.filter(
            is_active=True,
            start_date__lte=instance.start_time.date(),
            end_date__gte=instance.start_time.date()
        )
        
        for challenge in challenges:
            user_challenge, created = UserChallenge.objects.get_or_create(
                user=instance.user,
                challenge=challenge
            )
            user_challenge.update_progress()

@receiver(post_save, sender=DailyActivity)
def update_step_challenges(sender, instance, created, **kwargs):
    """Update step/distance challenges when daily activity is updated"""
    if created or instance.steps > 0 or instance.distance > 0:
        # Get all active challenges for this user
        challenges = instance.user.challenges.filter(
            is_active=True,
            start_date__lte=instance.date,
            end_date__gte=instance.date,
            target_type__in=[Challenge.STEPS, Challenge.DISTANCE]
        )
        
        for challenge in challenges:
            user_challenge, created = UserChallenge.objects.get_or_create(
                user=instance.user,
                challenge=challenge
            )
            user_challenge.update_progress()