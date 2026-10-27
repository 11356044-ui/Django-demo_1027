from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'student_id', 'department']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'student_id']
