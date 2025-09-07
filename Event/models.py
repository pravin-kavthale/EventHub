from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):

    CATEGORY_CHOICES = [
        ('music', 'Music'),
        ('art', 'Art'),
        ('sports', 'Sports'),
        ('tech', 'Tech'),
        ('travel', 'Travel'),
        ('other', 'Other'),
    ]

    title=models.CharField(max_length=100)
    description=models.TextField()
    category=models.CharField(max_length=100,choices=CATEGORY_CHOICES, default='other')
    date=models.DateTimeField()
    Location=models.CharField(max_length=300)
    start_time=models.TimeField()
    end_time=models.TimeField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    #relationship
    organizer=models.ForeignKey(User,on_delete=models.CASCADE,related_name='events_creater')
    participants=models.ManyToManyField(User,related_name='events_participated',blank=True)

     # optional image
    image = models.ImageField(upload_to="event_images/", default="event_images/default.png")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-start_time'] 

