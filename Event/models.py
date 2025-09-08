from django.db import models
from django.contrib.auth.models import User
import uuid

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

class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=self.slugify(self.name)
            super().save(*args,**kwargs)

    @property
    def popularity(self):
        return self.event_set.count()

    def __str__(self):
        return self.name


class Like(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    event_id=models.ForeignKey(Event,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usr.username} likes {self.event_id.title}'

class ChatRoom(models.Model):
    event=models.OneToOneField(Event,on_delete=models.CASCADE)
    users=models.ManyToManyField(User,related_name='chatrooms')
    name=models.CharField(max_length=100)

    def save(self,*args,**kwargs):
        if not self.name:
            self.name=f'chartroom_{self.event.id}'
            super().save(*args,**kwargs)

            self.users.add(self.event.participants.all())

class EventAttendence(models.Model):
    status_choices=[
        ('going','Going'),
        ('intersted','Intersted'),
        ('maybe','Maybe'),
        ('not_going','Not Going'),
    ]

    user=models.ForeignKey(User,on_delete=models.CASCADE, related_name="participations")
    event=models.ForeignKey(Event,on_delete=models.CASCADE,related_name="EventParticipants")
    status=models.CharField(max_length=10,choices=status_choices,default='pending')

    qr_token=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    attended=models.BooleanField(default=False)
    check_in_time=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"