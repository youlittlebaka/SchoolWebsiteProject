from django.urls import path

from . import views

app_name = 'lessons'

urlpatterns = [
    path('', views.lessons_home, name='lessons'),
    path('weekly-schedule/', views.lessons_home, name='weekly_schedule'),
    path('class/<int:stage_id>/schedule/', views.edit_stage_schedule, name='edit_stage_schedule'),
]
