from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
import uuid
from django.conf import settings

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Only JPG, JPEG, PNG, and GIF are supported.'))

def validate_video_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.mp4', '.mov', '.avi', '.webm']
    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Only MP4, MOV, AVI, and WEBM are supported.'))

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<type>/<filename>
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"user_{instance.user.id}/{instance.__class__.__name__.lower()}/{filename}"

def validate_image_size(file):
    max_size = 2 * 1024 * 1024  # 2 MB
    if file.size > max_size:
        raise ValidationError("Image file too large ( > 2MB ).")

def validate_video_size(file):
    max_size = 50 * 1024 * 1024  # 50 MB
    if file.size > max_size:
        raise ValidationError("Video file too large ( > 50MB ).")

def delete_old_file(file_field):
    """ Deletes old file from storage when replaced """
    if file_field and hasattr(file_field, 'path'):
        if os.path.isfile(file_field.path):
            os.remove(file_field.path)

