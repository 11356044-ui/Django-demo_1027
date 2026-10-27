from django.contrib import admin
from .models import Course, CourseTimeSlot, Enrollment, EnrollmentPeriod


class CourseTimeSlotInline(admin.TabularInline):
    model = CourseTimeSlot
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'name', 'teacher', 'credits', 'course_type', 'enrolled_count', 'capacity', 'is_full']
    list_filter = ['course_type', 'teacher']
    search_fields = ['course_code', 'name']
    inlines = [CourseTimeSlotInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at']
    list_filter = ['course', 'enrolled_at']
    search_fields = ['student__username', 'course__name']


@admin.register(EnrollmentPeriod)
class EnrollmentPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active']
