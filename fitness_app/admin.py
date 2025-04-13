# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'name', 'is_staff')
    search_fields = ('email', 'username', 'name')
    readonly_fields = ('date_joined', 'last_login')
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'username', 'bio', 'date_of_birth', 'gender', 'height', 'weight', 'profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Activity', {'fields': ('last_activity', 'current_streak', 'longest_streak', 'total_points')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(FollowRequest)
admin.site.register(Follow)
admin.site.register(WorkoutPlan)
admin.site.register(Exercise)
admin.site.register(WorkoutSession)
admin.site.register(WorkoutExercise)
admin.site.register(WorkoutMedia)
admin.site.register(DailyActivity)
admin.site.register(NutritionLog)
admin.site.register(ProgressPhoto)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Challenge)
admin.site.register(UserChallenge)
admin.site.register(Notification)