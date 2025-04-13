from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_future_date(value):
    """Validate that a date is not in the future"""
    from django.utils import timezone
    if value > timezone.now().date():
        raise ValidationError(_("Date cannot be in the future."))

def validate_image_size(value):
    """Validate that an image is not too large"""
    limit = 5 * 1024 * 1024  # 5MB
    if value.size > limit:
        raise ValidationError(_('Image too large. Size should not exceed 5MB.'))

def validate_video_size(value):
    """Validate that a video is not too large"""
    limit = 50 * 1024 * 1024  # 50MB
    if value.size > limit:
        raise ValidationError(_('Video too large. Size should not exceed 50MB.'))