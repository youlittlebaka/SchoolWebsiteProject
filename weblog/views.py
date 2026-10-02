from django .contrib import messages
from django.shortcuts import render
from .models import Weblog
def weblog(request):
    weblog = Weblog.objects.all()
    return render(request , 'weblog.html' , {'weblog': weblog})



def weblog_detail(request , pk):
    weblog = Weblog.objects.get(pk=pk)
    return render(request , 'weblog_detail.html', {'weblog': weblog})

def weblog_create(request):
    if request.method == 'GET':
        return render(request, 'weblog_create.html')
    if request.method != 'POST':
        messages.error(request , 'Invalid Request')
        return render(request , 'home.html')
    if not request.user.role == 'teacher' and not request.user.role == 'admin':
        messages.error(request , 'You are not authorized to create a weblog')
        return render(request , 'weblog.html')
    title = request.POST.get('title')
    content = request.POST.get('content')
    file = request.FILES.get('file')
    author = request.user
    published = request.POST.get('published') == 'on'
    category = request.POST.get('category')
    if not title or not content or not author or not category:
        messages.error(request , 'Title and content are required')
        return render(request , 'weblog_create.html')
    if category not in ['announcement', 'news', 'event', 'other']:
        messages.error(request , 'Invalid category')
        return render(request , 'weblog_create.html')
    weblog = Weblog.objects.create(
        title=title,
        content=content,
        author=author,
        file=file,
        published=published,
        category=category
    )
    
    weblog.save()
    messages.success(request , 'Weblog created successfully')
    return render(request , 'weblog_detail.html' , {'weblog': weblog})

def weblog_update(request , pk):
    if request.method != 'POST':
        messages.error(request , 'Invalid Request')
        return render(request , 'home.html')
    if not request.user.role == 'teacher' and not request.user.role == 'admin':
        messages.error(request , 'You are not authorized to update a weblog')
        return render(request , 'weblog.html')
    if weblog.author != request.user:
        if not request.user.role == 'admin':
            messages.error(request , 'You are not authorized to update this weblog')
            return render(request , 'weblog.html')
        title = request.POST.get('title')
        content = request.POST.get('content')
        file = request.FILES.get('file')
        published = request.POST.get('published') == 'on'
        category = request.POST.get('category')
        weblog.title = title
        weblog.content = content
        weblog.file = file
        weblog.published = published
        weblog.category = category
        weblog.save()
    messages.success(request , 'Weblog updated successfully')
    return render(request , 'weblog_detail.html' , {'weblog': weblog})

def weblog_delete(request , pk):
    if request.method != 'POST':
        messages.error(request , 'Invalid Request')
        return render(request , 'home.html')
    if not request.user.role == 'teacher' and not request.user.role == 'admin':
        messages.error(request , 'You are not authorized to update a weblog')
        return render(request , 'weblog.html')
    if weblog.author != request.user:
        if not request.user.role == 'admin':
            messages.error(request , 'You are not authorized to update this weblog')
            return render(request , 'weblog.html')
        weblog = Weblog.objects.get(pk=pk)
        weblog.delete()
        messages.success(request , 'Weblog deleted successfully')
        return render(request , 'weblog.html')
