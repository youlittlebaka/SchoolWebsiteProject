from django.db import models

from school import settings
    

class Weblog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='weblog_files/', blank=True, null=True)
    published = models.BooleanField(default=False)
    category = models.CharField(max_length=100, blank=True, null=True, choices=[
        ('announcement', 'Announcement'),
        ('news', 'News'),
        ('event', 'Event'),
        ('other', 'Other'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title
