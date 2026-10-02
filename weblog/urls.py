from django.urls import path

from . import views

app_name = 'weblog'

urlpatterns = [
    path('home/' , views.weblog , name='weblog'),
    path('<int:pk>/' , views.weblog_detail , name='weblog_detail'),
    path('create/' , views.weblog_create , name='weblog_create'),
    path('update/<int:pk>/' , views.weblog_update , name='weblog_update'),
    path('delete/<int:pk>/' , views.weblog_delete , name='weblog_delete'),
]