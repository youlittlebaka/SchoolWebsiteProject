from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from .models import ClassRoom , HomeWork
from django.contrib import messages ,  auth
from django.shortcuts import get_object_or_404
from .models import ClassRoom, Student 
from user.models import TeacherProfile as Teacher , ParentProfile as Parent
from lessons.models import Day, Lessons, Period, Stage


def _ensure_days_and_periods():
    day_values = [
        ("Monday", 1),
        ("Tuesday", 2),
        ("Wednesday", 3),
        ("Thursday", 4),
        ("Saturday", 5),
        ("Sunday", 6),
    ]
    period_values = [
        ("First Period", 1),
        ("Second Period", 2),
        ("Third Period", 3),
        ("Fourth Period", 4),
    ]

    for day_name, day_order in day_values:
        day_obj, _ = Day.objects.get_or_create(name=day_name, defaults={"order": day_order})
        if day_obj.order != day_order:
            day_obj.order = day_order
            day_obj.save(update_fields=["order"])

    for period_name, period_order in period_values:
        period_obj = Period.objects.filter(order=period_order).order_by("id").first()
        if period_obj is None:
            Period.objects.create(name=period_name, order=period_order)
        elif period_obj.name != period_name:
            period_obj.name = period_name
            period_obj.save(update_fields=["name"])

    days = Day.objects.filter(name__in=[item[0] for item in day_values]).order_by("order")
    periods = Period.objects.filter(order__in=[1, 2, 3, 4]).order_by("order", "id")[:4]
    return days, periods


def classroom_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login first')
        return render(request, 'login.html')

    # Get the logged-in student's profile
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'You are not a student.')
        return render(request, 'home.html')

    that_classroom = student_profile.class_room
    if that_classroom is None:
        messages.error(request, 'No classroom assigned yet.')
        return redirect('core:home')

    return redirect('students:classroom_detail', pk=that_classroom.pk)
def all_classrooms_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login first')
        return render(request, 'login.html')
    if not request.user.is_admin or not request.user.is_superuser:
        messages.error(request, 'You do not have permission for this action')
        return redirect('core:home')

    classrooms = ClassRoom.objects.all()
    return render(request, 'all_classes.html', {'classrooms': classrooms})

def homework_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login first')
        return render(request, 'login.html')


    HomeWork.delete_expired_homework()
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'You are not a student.')
        return render(request, 'error.html')

    # Get the student's class
    student_class = student_profile.class_room

    # Get homework assigned to that class
    that_homework = student_class.home_work.all()  # ManyToManyField in ClassRoom

    return render(request, 'homework.html', {'that_homework': that_homework})


def add_homework(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request')
        return redirect('core:home')

    if not (request.user.is_teacher or request.user.is_admin or request.user.is_superuser):
        messages.error(request, 'You do not have permission for this action')
        return redirect('core:home')

    title = (request.POST.get('title') or '').strip()
    description = (request.POST.get('description') or '').strip()
    classroom_id = (request.POST.get('classroom') or request.POST.get('classroom_id') or '').strip()
    course_id = (request.POST.get('course') or '').strip()

    if not all([title, description, classroom_id]):
        messages.error(request, 'All fields are required')
        ref_pk = request.POST.get('classroom_id') or request.POST.get('classroom')
        if ref_pk and str(ref_pk).isdigit():
            return redirect('students:classroom_detail', pk=int(ref_pk))
        return redirect('core:home')

    classroom = get_object_or_404(ClassRoom, pk=classroom_id)

    # simple teacher rule
    if request.user.is_teacher:
        teacher_profile = request.user.teacher_profile
    else:
        teacher_profile = classroom.teacher.first()
        if teacher_profile is None:
            messages.error(request, 'This class has no teacher.')
            return redirect('students:classroom_detail', pk=classroom.pk)

    # simple course rule

    homework = HomeWork.objects.create(
        title=title,
        teacher=teacher_profile,
        description=description,
    )

    # Assign homework to classroom
    classroom.home_work.add(homework)

    messages.success(request, 'Homework added successfully')
    return redirect('students:classroom_detail', pk=classroom.pk)


def add_classroom(request):
    if not request.user.role == 'admin' or not request.user.is_superuser:
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    
    all_teachers = Teacher.objects.all()
    all_students = Student.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        class_grade = request.POST.get('class_grade')
        teacher = request.POST.get('teacher')
        students = request.POST.getlist('students')  
        if not name or not class_grade:
            messages.error(request , 'all fields of the class is required')
            return render(request , 'add_class.html', {
                'all_teachers': all_teachers,
                'all_students': all_students
            })
        classroom = ClassRoom.objects.create(
            name = name ,
            class_grade = class_grade ,
        )
        classroom.teacher.set(request.POST.getlist('teachers'))
        for student in Student.objects.filter(pk__in=students):
            student.class_room = classroom
            student.save()
        messages.success(request , 'classroom added successfully')
        return redirect('students:all_classes')
    
    # For GET request
    return render(request , 'add_class.html', {
        'all_teachers': all_teachers,
        'all_students': all_students
    })


def edit_classroom(request , pk):
    if request.method != 'POST' :
        messages.error(request , 'invalid request')
        return render(request , 'home.html')
    if not request.user.role == 'admin' or not request.user.is_superuser:
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    that_class = ClassRoom.objects.filter(pk=pk)
    name = request.POST.get('name')
    teachers = request.POST.get('teachers')
    class_grade = request.POST.get('class_grade')
    

def edit_homework(request , pk):
    pass

def remove_classroom(request , pk):
    if not request.user.role == 'admin' or not request.user.is_superuser:
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    classroom = get_object_or_404(ClassRoom, pk=pk)
    
    # Remove all students from this classroom first
    Student.objects.filter(class_room=classroom).update(class_room=None)
    
    # Now delete the classroom
    classroom.delete()
    messages.success(request , 'deleted successfully')
    return redirect('students:all_classes')

def remove_home_work(request , pk):
    if request.method != 'POST' :
        messages.error(request , 'invalid request')
        return render(request , 'home.html')
    if not request.user.role == 'admin' or not request.user.is_superuser or not request.user.is_teacher:
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    homework = get_object_or_404(HomeWork, pk=pk)
    homework.delete()
    messages.success(request , 'deleted successfully')
    return redirect('students:all_classes')

def homework_detail(request , pk):
    if not request.user.role == 'admin' or not request.user.is_superuser:
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    homework = HomeWork.objects.filter(pk=pk)
    return render(request , 'homework_detail.html' , {'homework' : homework})

def classroom_detail(request , pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Login first')
        return redirect('user:login')

    classroom = get_object_or_404(ClassRoom, pk=pk)

    is_admin_user = request.user.is_admin or request.user.is_superuser
    is_teacher_class_owner = request.user.is_teacher and classroom.teacher.filter(user=request.user).exists()

    is_student_of_this_class = False
    if request.user.is_student:
        try:
            is_student_of_this_class = request.user.student_profile.class_room_id == classroom.id
        except Exception:
            is_student_of_this_class = False

    if not (is_admin_user or is_teacher_class_owner or is_student_of_this_class):
        messages.error(request, 'you do not have right premisions for this action')
        return redirect('core:home')

    can_edit = is_admin_user or is_teacher_class_owner

    stage, _ = Stage.objects.get_or_create(name=classroom.name)
    days, periods = _ensure_days_and_periods()

    existing_lessons = {
        (lesson.day_id, lesson.period_id): lesson
        for lesson in Lessons.objects.filter(stage=stage, day__in=days, period__in=periods)
    }

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "You do not have permission to edit this schedule.")
            return redirect("students:classroom_detail", pk=classroom.pk)

        for day in days:
            for period in periods:
                field_name = f"slot_{day.id}_{period.id}"
                lesson_name = request.POST.get(field_name, "").strip()
                current_lesson = existing_lessons.get((day.id, period.id))

                if lesson_name:
                    if current_lesson:
                        if current_lesson.lesson_name != lesson_name:
                            current_lesson.lesson_name = lesson_name
                            current_lesson.save(update_fields=["lesson_name"])
                    else:
                        Lessons.objects.create(
                            stage=stage,
                            day=day,
                            period=period,
                            lesson_name=lesson_name,
                        )
                elif current_lesson:
                    current_lesson.delete()

        messages.success(request, "Class schedule saved.")
        return redirect("students:classroom_detail", pk=classroom.pk)

    grid_rows = []
    for day in days:
        row_cells = []
        for period in periods:
            existing = existing_lessons.get((day.id, period.id))
            row_cells.append(
                {
                    "field_name": f"slot_{day.id}_{period.id}",
                    "value": existing.lesson_name if existing else "",
                }
            )
        grid_rows.append({"day": day, "cells": row_cells})

    return render(
        request,
        "classroom.html",
        {
            "classroom": classroom,
            "stage": stage,
            "periods": periods,
            "grid_rows": grid_rows,
            "can_edit": can_edit,
            "homework_list": classroom.home_work.all().order_by("-created_at"),
        },
    )

def all_classes(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Login first')
        return render(request, 'login.html')
    if not request.user.role == 'admin' or not request.user.is_superuser:
        messages.error(request, 'You do not have permission for this action')
        return redirect('core:home')

    classrooms = ClassRoom.objects.all().order_by('name')
    print(f"DEBUG: Found {classrooms.count()} classrooms")
    return render(request, 'all_classes.html', {'classrooms': classrooms})

def my_students(request):
    if not request.user.role == 'teacher':
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    teacher = request.user.teacher_profile
    students = Student.objects.filter(class_room__home_work__teacher=teacher).distinct()
    return render(request , 'my_students.html' , {'students' : students})

def my_children(request):
    if not request.user.role == 'parent':
        messages.error(request , 'you do not have right premisions for this action')
        return redirect('core:home')
    parent = request.user.parent_profile
    children = parent.children.all()
    return render(request , 'my_children.html' , {'children' : children})
