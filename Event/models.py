from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="events")
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_created')
    participants = models.ManyToManyField(User, related_name='events_participated', blank=True)

    image = models.ImageField(upload_to="event_images/", default="event_images/default.png")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_time']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} likes {self.event.title}'


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

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

class Message(models.Model):
    chatroom=models.ForeignKey(chatroom,on_delete=models.CASCADE,related_name="messages")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}: {self.content}'
