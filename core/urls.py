from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('' , views.home , name='home'),
    path('help/contact_us/' , views.contact_us , name='contact_us'),
    path('help/about_us/' , views.about_us , name='about_us'),
    path('help/' , views.help_page , name='help'),
]