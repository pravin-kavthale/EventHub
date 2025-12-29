from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from django.utils import timezone

from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    favicon = models.ImageField(upload_to='category_favicons/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def popularity(self):
        return self.events.count()

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    comments_enabled = models.BooleanField(default=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="events"
    )

    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    start_time = models.TimeField()
    end_time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="events_created"
    )

    participants = models.ManyToManyField(
        User,
        related_name="joined_events",
        blank=True
    )

    
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} likes {self.event.title}"

class ChatRoom(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='chatrooms')
    name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f'chatroom_{self.event.id}'
        super().save(*args, **kwargs)
        self.users.add(*self.event.participants.all())

    def __str__(self):
        return self.name

class EventAttendance(models.Model):
    STATUS_CHOICES = [
        ('going', 'Going'),
        ('interested', 'Interested'),
        ('maybe', 'Maybe'),
        ('not_going', 'Not Going'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='maybe')

    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    attended = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'event')   # prevent duplicate likes

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

class Message(models.Model):
    chatroom=models.ForeignKey(ChatRoom,on_delete=models.CASCADE,related_name="messages")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.user.username}: {self.content}'

class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    event=models.ForeignKey("Event",on_delete=models.CASCADE,related_name="comments")
    parent=models.ForeignKey("self",null=True,blank=True,on_delete=models.CASCADE,related_name="replies")
    content=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} on {self.event.title}: {self.content[:30]}"

    class Meta:
        ordering=["-created_at"]
        
    def is_reply(self):
        return self.parent is not None
    

class Report(models.Model):
    REPORT_REASON_CHOICES=[
        ('spam','spam or misleading'),
        ('inappropriate','inappropriate content'),
        ('harassment','harassment or hate speech'),
        ('other','other'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    event=models.ForeignKey(Event,on_delete=models.CASCADE,related_name="reports")
    reason=models.CharField(max_length=20,choices=REPORT_REASON_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reported {self.event.title} for {self.reason}"
    class Meta:
        ordering=["-created_at"]
