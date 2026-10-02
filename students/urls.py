from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('classroom/' , views.classroom_view , name='classroom'),
    path('classroom/home_work/' , views.homework_view , name='homework_view'),
    path('add/classroom/' , views.add_classroom , name='add_classroom'),
    path('add/homework/' , views.add_homework , name='add_homework'),
    path('edit/classroom/<int:pk>/' , views.edit_classroom , name='edit_classroom'),
    path('edit/homework/<int:pk>/' ,views.edit_homework , name='edit_homework'),
    path('remove/homework/<int:pk>/' ,views.remove_home_work , name='remove_homework'),
    path('remove/classroom/<int:pk>/' , views.remove_classroom , name='remove_classroom'),
    path('homework_detail/<int:pk>/' , views.homework_detail , name='homework_detail'),
    path('classroom_detail/<int:pk>/' , views.classroom_detail , name='classroom_detail'),
    path('all_classes/' , views.all_classes , name='all_classes'),
    path('my_students/' , views.my_students , name='my_students'),
    path('my_children/' , views.my_children , name='my_children'),
    path('all_classrooms/' , views.all_classrooms_view , name='all_classrooms'),
]
