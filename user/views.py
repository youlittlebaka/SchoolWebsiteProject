from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from .models import User , TeacherProfile , ParentProfile , StaffProfile
from .models import Message, MessageRecipient
from django.contrib.auth import get_user_model
from students.models import ClassRoom , Student , HomeWork 
from django.contrib import messages ,  auth
from django.shortcuts import get_object_or_404
from django.db.models import Q
from lessons.models import Lessons
from datetime import date

# Create your views here.
def add_user(request):
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('core:home')

    if request.method == 'POST':
        data = request.POST

        required = ['full_name','national_id','phone','home_address',
                    'home_phone','date_born','role','gender']

        if not all(data.get(k) for k in required):
            messages.error(request,'All fields required')
            return redirect('user:add_user')

        if User.objects.filter(national_id=data['national_id']).exists():
            messages.error(request,'User exists')
            return redirect('user:add_user')

        user = User.objects.create_user(
            full_name=data['full_name'],
            national_id=data['national_id'],
            phone=data['phone'],
            home_address=data['home_address'],
            home_phone=data['home_phone'],
            date_born=data['date_born'],
            role=data['role'],
            gender=data['gender'],
            password=data['national_id'],
        )

        # redirect student to classroom assignment

        messages.success(request,'User created')
        return redirect('user:all_students')

    return render(request,'add_user.html')





def auth_page(request):
    if request.user.is_authenticated:
        messages.error(request , 'you are loged in')
        return render(request , 'home.html')
    else:
        return render(request , 'auth_page.html')




def login_view(request):
    if request.user.is_authenticated:
        messages.error(request , 'you are already loged in')
        return render(request , 'home.html')
    else:

        if request.method != 'POST':
            messages.error(request , 'invalid request')
            return render(request , 'home.html')
        else:

            national_id = request.POST.get('national_id')
            password = request.POST.get('password')

            if not all([national_id , password]):
                messages.error(request , 'all fields are required')
                return redirect('user:auth_page')
            user = authenticate(
                request ,
                national_id = national_id , 
                password = password ,
            )
            if user is None:
                messages.error(request , 'no user found')
                return redirect('user:auth_page')
            login(request , user)
            messages.success(request , 'loged in succesfully')
            return redirect('user:profile')
        
def profile(request):
    if not request.user.is_authenticated:
        messages.error(request , 'login first')
        return redirect('user:login_view')
    the_user = request.user
    student_profile = None
    teacher_profile = None
    student_parents = []

    if the_user.is_student:
        try:
            student_profile = the_user.student_profile
            student_parents = student_profile.parents.select_related('user').all()
        except Exception:
            student_profile = None
            student_parents = []

    if the_user.is_teacher:
        try:
            teacher_profile = the_user.teacher_profile
        except Exception:
            teacher_profile = None

    return render(
        request,
        'profile.html',
        {
            'the_user': the_user,
            'student_profile': student_profile,
            'teacher_profile': teacher_profile,
            'student_parents': student_parents,
        },
    )



def logout_view(request):
    logout(request)
    messages.success(request , 'loged out succesfully')
    return redirect('user:login')



def profile_edit(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You have to login first')
        return redirect('login')   # use URL name, not template path

    if not request.user.is_admin or not request.user.is_superuser:
        messages.error(request, 'You do not have permissions for this action')
        return redirect('home')    # redirect instead of render

    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name', user.full_name)
        user.phone = request.POST.get('phone', user.phone)
        user.home_address = request.POST.get('home_address', user.home_address)
        user.home_phone = request.POST.get('home_phone', user.home_phone)
        user.is_active = request.POST.get('is_active')
        user.role = request.POST.get('role', user.role)
        user.student_profile.grade = request.POST.get('grade', user.student_profile.grade)
        user.teacher_profile.education = request.POST.get('education', user.teacher_profile.education)
        user.student_profile.parents.set(request.POST.getlist('parents'))  # Assuming parents is a ManyToManyField
        user.student_profile.teacher.set(request.POST.getlist('teacher'))
        user.student_profile.lessons.set(request.POST.getlist('lessons'))
        user.student_profile.class_room = request.POST.get('class_room', user.student_profile.class_room)
        user.student_profile.report_card = request.POST.get('report_card', user.student_profile.report_card)
        user.student_profile.is_paid = request.POST.get('is_paid', user.student_profile.is_paid) == 'on'


        user.save()
        messages.success(request, 'Changed successfully')
        return redirect('user:user_detail', pk=user.pk)

    return redirect('home')  # invalid request fallback

def edit_profile(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You have to login first')
        return redirect('login')
    if request.user.pk != pk:
        messages.error(request, 'You can only edit your own profile')
        return redirect('home')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        pfp = request.FILES.get('pfp')
        if pfp:
            user.pfp = pfp
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('user:profile')

def user_detail(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'you have to login first')
        return redirect('user:login')

    if not request.user.role == 'teacher' and not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, 'you do not have permissions for this action')
        return redirect('core:home')

    that_user = get_object_or_404(User, pk=pk)
    # Calculate age from date_born
    age = None
    if that_user.date_born:
        today = date.today()
        birthday = that_user.date_born
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    # Initialize
    student_profile = None
    student_parents = []
    student_teacher = []

    # Only if the user has a student_profile
    if hasattr(that_user, 'student_profile') and that_user.student_profile:
        student_profile = that_user.student_profile
        student_parents = student_profile.parents.select_related('user').all()
        # Only if teacher relation exists
        if hasattr(student_profile, 'teacher') and student_profile.teacher:
            student_teacher = student_profile.teacher.select_related('user').all()

    return render(
        request,
        'user_detail.html',
        {
            'that_user': that_user,
            'student_profile': student_profile,
            'student_parents': student_parents,
            'student_teacher': student_teacher,
            'lessons': Lessons.objects.all(),
            'age': age,
        }
    )



def remove_user(request , pk):
    if request.method != 'POST':
        messages.error(request , 'invalid request')
        return render(request , 'home.html')
    if not request.user.is_admin or not request.user.is_superuser:
        messages.error(request , 'you do not have premisions for this action')
        return redirect('core:home')
    the_user = get_object_or_404(User , pk=pk)
    the_user.delete()
    messages.success(request , 'user deleted successfully')
    return redirect('core:home')

def all_students(request):
    if not request.user.is_authenticated:
        messages.error(request , 'you have to login first')
        return redirect('user:login')
    if not request.user.is_teacher and not request.user.is_admin and not request.user.is_superuser:
        messages.error(request , 'you do not have premisions for this action')
        return redirect('core:home')
    q = request.GET.get('q', '').strip()
    students = User.objects.filter(role='student')

    if q:
        students = students.filter(
            Q(full_name__icontains=q)
            | Q(national_id__icontains=q)
            | Q(phone__icontains=q)
            | Q(home_phone__icontains=q)
        )

    students = students.order_by('full_name')
    return render(request , 'all_students.html' , {'students':students, 'q': q})


def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('core:home')
    
    from students.models import Student, ClassRoom
    from user.models import TeacherProfile
    from django.contrib.admin.models import LogEntry
    
    users = User.objects.all()
    students = Student.objects.all()
    teachers = TeacherProfile.objects.all()
    classrooms = ClassRoom.objects.all()
    logs = LogEntry.objects.all().order_by('-action_time')
    user = request.user
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        logs = logs.filter(action_time__date__gte=date_from)
    if date_to:
        logs = logs.filter(action_time__date__lte=date_to)
    
    return render(request, 'admin_panel.html', {
        'user': user,
        'users': users,
        'students': students,
        'teachers': teachers,
        'classrooms': classrooms,
        'logs': logs,
        'date_from': date_from,
        'date_to': date_to
    })

def message_sender(request):
    if not request.user.is_authenticated:
        messages.error(request , 'you have to login first')
        return redirect('user:login')
    if not request.user.is_teacher and not request.user.is_admin and not request.user.is_superuser:
        messages.error(request , 'you do not have premisions for this action')
        return redirect('core:home')
    
    if request.method == 'POST':
        sender = request.user
        # keep the form field name 'recipiant' to stay compatible with existing templates
        recipient_ids = request.POST.getlist('recipiant')
        attachment = request.FILES.get('attachment')
        subject = request.POST.get('subject')
        is_announcement = request.POST.get('is_announcement') == 'on'
        body = request.POST.get('body')

        User = get_user_model()

        # Create one Message and link recipients via MessageRecipient
        message = Message.objects.create(
            sender=sender,
            subject=subject,
            body=body,
            attachment=attachment,
            is_announcement=is_announcement,
        )

        for rid in recipient_ids:
            try:
                recipient_user = User.objects.get(pk=int(rid))
            except (User.DoesNotExist, ValueError):
                continue

            MessageRecipient.objects.create(
                message=message,
                recipient=recipient_user,
            )

        messages.success(request, 'Message sent successfully!')
        return redirect('user:admin_panel')
    
    return render(request, 'admin_panel.html')

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required



def inbox_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    inbox = (
        MessageRecipient.objects
        .filter(recipient=request.user, is_deleted=False)
        .select_related('message', 'message__sender')
        .order_by('-message__created_at')
    )

    data = []
    unread = 0

    for item in inbox:
        if not item.is_read:
            unread += 1

        data.append({
            "id": item.id,
            "subject": item.message.subject,
            "date": item.message.created_at.strftime("%Y-%m-%d %H:%M"),
            "is_read": item.is_read
        })

    return JsonResponse({
        "messages": data,
        "unread": unread
    })



def inbox_detail_api(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    link = get_object_or_404(
        MessageRecipient,
        pk=pk,
        recipient=request.user,
        is_deleted=False
    )

    link.mark_as_read()

    m = link.message

    return JsonResponse({
        "id": link.id,
        "subject": m.subject,
        "body": m.body,
        "sender": m.sender.full_name,
        "date": m.created_at.strftime("%Y-%m-%d %H:%M"),
        "attachment": m.attachment.url if m.attachment else None
    })

def message_detail(request, pk):
    if not request.user.is_authenticated:
        messages.error(request , 'you have to login first')
        return redirect('user:login')
    if not request.user.is_teacher and not request.user.is_admin and not request.user.is_superuser:
        messages.error(request , 'you do not have premisions for this action')
        return redirect('core:home')
    
    message = get_object_or_404(Message, pk=pk)
    return render(request, 'message_detail.html', {'message': message})