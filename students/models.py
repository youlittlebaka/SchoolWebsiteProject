from django.conf import settings
from django.db import models
from lessons.models import Lessons
from user.models import User , TeacherProfile
from datetime import datetime , timedelta
from django.utils import timezone
from django.conf import settings
from django.db import models




class HomeWork(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        'user.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='homeworks'
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    @classmethod
    def delete_expired_homework(cls):
        expiry_time = timezone.now() - timedelta(hours=24)
        cls.objects.filter(created_at__lte=expiry_time).delete()


class ClassRoom(models.Model):
    name = models.CharField(max_length=5)
    teacher = models.ManyToManyField(
        'user.TeacherProfile',
        related_name='classrooms',
        blank=True,
    )
    lessons = models.ManyToManyField('lessons.Lessons', blank=True)
    home_work = models.ManyToManyField(HomeWork  , blank=True)
    class_grade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ('first_grade', 'First Grade'),
            ('second_grade', 'Second Grade'),
            ('third_grade', 'Third Grade'),
            ('fourth_grade', 'Fourth Grade'),
            ('fifth_grade', 'Fifth Grade'),
            ('sixth_grade', 'Sixth Grade'),
            ('seventh_grade', 'Seventh Grade'),
            ('eighth_grade', 'Eighth Grade'),
            ('ninth_grade', 'Ninth Grade'),
            ('tenth_grade', 'Tenth Grade'),
            ('eleventh_grade', 'Eleventh Grade'),
            ('twelfth_grade', 'Twelfth Grade'),]
)



class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    parents = models.ManyToManyField(
        'user.ParentProfile',
        blank=True,
        related_name='students'
    )

    teacher = models.ForeignKey(
        'user.TeacherProfile',
        blank=True,
        on_delete=models.PROTECT,
        related_name='students',
        null=True,
    )

    grade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=[
            ('first_grade', 'First Grade'),
            ('second_grade', 'Second Grade'),
            ('third_grade', 'Third Grade'),
            ('fourth_grade', 'Fourth Grade'),
            ('fifth_grade', 'Fifth Grade'),
            ('sixth_grade', 'Sixth Grade'),
            ('seventh_grade', 'Seventh Grade'),
            ('eighth_grade', 'Eighth Grade'),
            ('ninth_grade', 'Ninth Grade'),
            ('tenth_grade', 'Tenth Grade'),
            ('eleventh_grade', 'Eleventh Grade'),
            ('twelfth_grade', 'Twelfth Grade'),
        ]
    )
    class_room = models.ForeignKey(ClassRoom , on_delete=models.PROTECT , related_name='students' , null=True , blank=True)
    report_card = models.TextField(blank=True, null=True)
    is_paid = models.BooleanField(default=True)
    

    def moms(self):
        return self.parents.filter(user__gender='female')

    def dads(self):
        return self.parents.filter(user__gender='male')

