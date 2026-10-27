from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Course, Enrollment, EnrollmentPeriod
from accounts.models import Profile


def is_enrollment_period_open():
    now = timezone.now()
    periods = EnrollmentPeriod.objects.filter(is_active=True)
    for period in periods:
        if period.start_time <= now <= period.end_time:
            return True
    return False


def has_time_conflict(student, course):
    student_enrollments = Enrollment.objects.filter(student=student)
    for enrollment in student_enrollments:
        for slot in enrollment.course.time_slots.all():
            for new_slot in course.time_slots.all():
                if slot.day_of_week == new_slot.day_of_week:
                    # Check if time ranges overlap
                    if not (slot.end_time <= new_slot.start_time or new_slot.end_time <= slot.start_time):
                        return True
    return False


def course_list(request):
    query = request.GET.get('q', '')
    grade_filter = request.GET.get('grade', '')
    courses = Course.objects.all().prefetch_related('time_slots')
    
    if query:
        courses = courses.filter(
            Q(course_code__icontains=query) | 
            Q(name__icontains=query) |
            Q(teacher__username__icontains=query)
        )
    
    if grade_filter:
        courses = courses.filter(grade=grade_filter)
    
    # Get student's enrolled courses if logged in
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    
    context = {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids,
        'query': query,
        'grade_filter': grade_filter,
        'enrollment_open': is_enrollment_period_open(),
        'grade_choices': Course.GRADE_CHOICES,
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        if not is_enrollment_period_open():
            messages.error(request, '目前不在選課期間內。')
            return redirect('course_list')
        
        course = get_object_or_404(Course, pk=course_id)
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, '你已經選修過這門課了。')
            return redirect('course_list')
        
        # Check capacity
        if course.is_full:
            messages.error(request, '此課程已額滿。')
            return redirect('course_list')
        
        # Check time conflict
        if has_time_conflict(request.user, course):
            messages.error(request, '與已選課程時段衝突。')
            return redirect('course_list')
        
        # Enroll
        Enrollment.objects.create(student=request.user, course=course)
        course.enrolled_count += 1
        course.save()
        messages.success(request, f'成功加選 {course.name}。')
        return redirect('course_list')
    
    return redirect('course_list')


@login_required
def drop_course(request, course_id):
    if request.method == 'POST':
        if not is_enrollment_period_open():
            messages.error(request, '目前不在選課期間內。')
            return redirect('course_list')
        
        course = get_object_or_404(Course, pk=course_id)
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        
        if not enrollment:
            messages.warning(request, '你並未選修這門課。')
            return redirect('course_list')
        
        enrollment.delete()
        course.enrolled_count = max(0, course.enrolled_count - 1)
        course.save()
        messages.success(request, f'成功退選 {course.name}。')
        return redirect('course_list')
    
    return redirect('course_list')


@login_required
def my_schedule(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course').prefetch_related('course__time_slots')
    courses = [e.course for e in enrollments]
    
    context = {
        'enrollments': enrollments,
        'courses': courses,
    }
    return render(request, 'courses/my_schedule.html', context)


def course_detail(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related('time_slots', 'teacher'), pk=course_id)
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    context = {
        'course': course,
        'enrolled': enrolled,
        'enrollment_open': is_enrollment_period_open(),
    }
    return render(request, 'courses/course_detail.html', context)
