from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('auth_page' , views.auth_page , name='auth_page'),
    path('add/user/', views.add_user, name='add_user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit/profile/<int:pk>/', views.profile_edit, name='profile_edit'),
    path('remove/user/<int:pk>/', views.remove_user, name='remove_user'),
    path('user_detail/<int:pk>/' , views.user_detail , name='user_detail'),
    path('all_students/' , views.all_students , name='all_students'),
    path('admin_panel/' , views.admin_panel , name='admin_panel'),
    path('message_sender/' , views.message_sender , name='message_sender'),
    path('message_detail/<int:pk>/', views.message_detail, name='message_detail'),
    path('inbox/api/', views.inbox_api, name='inbox_api'),
    path('inbox/<int:pk>/', views.inbox_detail_api, name='inbox_detail_api'),
    path('edit_profile/<int:pk>/', views.edit_profile, name='edit_profile'),

]