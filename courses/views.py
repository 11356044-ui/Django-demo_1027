from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Course, Enrollment, EnrollmentPeriod, CourseTimeSlot
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
                    if not (slot.end_time <= new_slot.start_time or new_slot.end_time <= slot.start_time):
                        return True
    return False


def get_user_role(user):
    if hasattr(user, 'profile'):
        return user.profile.role
    return None


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
        
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, '你已經選修過這門課了。')
            return redirect('course_list')
        
        if course.is_full:
            messages.error(request, '此課程已額滿。')
            return redirect('course_list')
        
        if has_time_conflict(request.user, course):
            messages.error(request, '與已選課程時段衝突。')
            return redirect('course_list')
        
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
    
    context = {
        'enrollments': enrollments,
    }
    return render(request, 'courses/my_schedule.html', context)


def course_detail(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related('time_slots'), pk=course_id)
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    context = {
        'course': course,
        'enrolled': enrolled,
        'enrollment_open': is_enrollment_period_open(),
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def teacher_course_list(request):
    role = get_user_role(request.user)
    if role != 'teacher' and not request.user.is_staff:
        return HttpResponseForbidden('僅限教師或管理員使用')
    
    if request.user.is_staff and role != 'teacher':
        courses = Course.objects.all().prefetch_related('time_slots', 'enrollments__student')
    else:
        courses = Course.objects.filter(teacher=request.user).prefetch_related('time_slots', 'enrollments__student')
    context = {
        'courses': courses,
    }
    return render(request, 'courses/teacher_course_list.html', context)


@login_required
def teacher_course_create(request):
    role = get_user_role(request.user)
    if role != 'teacher' and not request.user.is_staff:
        return HttpResponseForbidden('僅限教師或管理員使用')
    
    if request.method == 'POST':
        course_code = request.POST.get('course_code', '').strip()
        name = request.POST.get('name', '').strip()
        credits = request.POST.get('credits') or 2
        course_type = request.POST.get('course_type') or 'elective'
        grade = request.POST.get('grade') or None
        capacity = request.POST.get('capacity') or 30
        description = request.POST.get('description', '')
        objectives = request.POST.get('objectives', '')
        syllabus = request.POST.get('syllabus', '')
        
        if not course_code or not name:
            messages.error(request, '課程代碼與課程名稱為必填欄位')
            context = {
                'course_type_choices': Course.COURSE_TYPE_CHOICES,
                'grade_choices': Course.GRADE_CHOICES,
            }
            return render(request, 'courses/teacher_course_create.html', context)
        
        if Course.objects.filter(course_code=course_code).exists():
            messages.error(request, '此課程代碼已存在，請使用其他代碼')
            context = {
                'course_type_choices': Course.COURSE_TYPE_CHOICES,
                'grade_choices': Course.GRADE_CHOICES,
            }
            return render(request, 'courses/teacher_course_create.html', context)
        
        course = Course.objects.create(
            course_code=course_code,
            name=name,
            teacher=request.user,
            credits=int(credits),
            course_type=course_type,
            grade=int(grade) if grade else None,
            capacity=int(capacity),
            description=description,
            objectives=objectives,
            syllabus=syllabus,
        )
        messages.success(request, f'成功新增課程「{course.name}」')
        return redirect('teacher_course_list')
    
    context = {
        'course_type_choices': Course.COURSE_TYPE_CHOICES,
        'grade_choices': Course.GRADE_CHOICES,
    }
    return render(request, 'courses/teacher_course_create.html', context)


@login_required
def teacher_course_edit(request, course_id):
    role = get_user_role(request.user)
    if role != 'teacher' and not request.user.is_staff:
        return HttpResponseForbidden('僅限教師或管理員使用')
    
    course = get_object_or_404(Course, pk=course_id)
    if course.teacher != request.user and not request.user.is_staff:
        return HttpResponseForbidden('只能管理自己開設的課程')
    
    if request.method == 'POST':
        course.name = request.POST.get('name', course.name)
        course.description = request.POST.get('description', '')
        course.objectives = request.POST.get('objectives', '')
        course.syllabus = request.POST.get('syllabus', '')
        course.save()
        messages.success(request, '課程資料已更新')
        return redirect('teacher_course_list')
    
    context = {
        'course': course,
    }
    return render(request, 'courses/teacher_course_edit.html', context)


@login_required
def teacher_course_students(request, course_id):
    role = get_user_role(request.user)
    if role != 'teacher' and not request.user.is_staff:
        return HttpResponseForbidden('僅限教師或管理員使用')
    
    course = get_object_or_404(Course, pk=course_id)
    if course.teacher != request.user and not request.user.is_staff:
        return HttpResponseForbidden('只能查看自己開設的課程')
    
    enrollments = Enrollment.objects.filter(course=course).select_related('student', 'student__profile')
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'courses/teacher_course_students.html', context)
