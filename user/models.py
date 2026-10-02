from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, national_id, password=None, **extra_fields):
        if not national_id:
            raise ValueError("national_id required")

        user = self.model(national_id=national_id, **extra_fields)
        user.set_password(password or national_id)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, national_id, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(national_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
    ]

    full_name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=20 , null=True , blank=True)
    home_address = models.CharField(max_length=255 , null=True , blank=True)
    home_phone = models.CharField(max_length=20 , null=True , blank=True)
    date_born = models.DateField(null=True , blank=True)
    gender = models.CharField(max_length=10, choices=[('man','Male'),('woman','Female')])

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'national_id'
    REQUIRED_FIELDS = ['full_name' , 'gender' , 'role']
    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    # Role properties
    @property
    def is_student(self): return self.role == 'student'

    @property
    def is_teacher(self): return self.role == 'teacher'

    @property
    def is_parent(self): return self.role == 'parent'

    @property
    def is_admin(self): return self.role == 'admin'

    @property
    def is_staff_member(self): return self.role == 'staff'


class TeacherProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    education = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.full_name


class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name


class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name
    
class adminprofile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name
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
    elif instance.role == 'admin':
        StaffProfile.objects.get_or_create(user = instance)
    elif instance.role == 'student':
        from students.models import Student
        Student.objects.get_or_create(user=instance)



from django.conf import settings
from django.db import models
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sent_messages",
    )
    subject = models.CharField(max_length=120)
    body = models.TextField()
    attachment = models.FileField(upload_to="messages/", blank=True, null=True)
    is_announcement = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} from {self.sender.full_name}"


class MessageRecipient(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="recipients",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inbox_links",
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["message", "recipient"],
                name="unique_message_recipient"
            )
        ]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "is_deleted"]),
        ]

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def __str__(self):
        return f"Message to {self.recipient.full_name} | {self.message.subject}"
