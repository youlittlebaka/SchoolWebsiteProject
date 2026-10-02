from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TeacherProfile, ParentProfile, StaffProfile


@receiver(post_save, sender=User)
def create_profiles(sender, instance, **kwargs):
    if instance.role == 'teacher':
        TeacherProfile.objects.get_or_create(user=instance)

    elif instance.role == 'parent':
        ParentProfile.objects.get_or_create(user=instance)

    elif instance.role == 'staff':
        StaffProfile.objects.get_or_create(user=instance)
