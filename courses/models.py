from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('required', '必修'),
        ('elective', '選修'),
        ('general', '通識'),
    ]
    GRADE_CHOICES = [
        (1, '一年級'),
        (2, '二年級'),
        (3, '三年級'),
        (4, '四年級'),
    ]
    
    course_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_teaching')
    credits = models.IntegerField(default=2)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='elective')
    grade = models.IntegerField(choices=GRADE_CHOICES, null=True, blank=True, verbose_name='適用年級')
    capacity = models.IntegerField(default=30)
    enrolled_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.course_code} - {self.name}"
    
    @property
    def is_full(self):
        return self.enrolled_count >= self.capacity
    
    @property
    def available_slots(self):
        return self.capacity - self.enrolled_count


class CourseTimeSlot(models.Model):
    DAY_CHOICES = [
        (1, '星期一'),
        (2, '星期二'),
        (3, '星期三'),
        (4, '星期四'),
        (5, '星期五'),
        (6, '星期六'),
        (7, '星期日'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.course.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time} @ {self.classroom}"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('結束時間必須晚於開始時間')


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.username} - {self.course.name}"


class EnrollmentPeriod(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('結束時間必須晚於開始時間')
