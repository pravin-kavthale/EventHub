from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from Event.models import Event

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    FullName = models.TextField(max_length=30, blank=True)
    Bio = models.TextField(blank=True)
    Age = models.PositiveIntegerField(null=True, blank=True)
    Gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True
    )
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    MobileNumber = models.PositiveIntegerField(null=True, blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.image.path)
   
class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    message = models.CharField(max_length=255)
    action_url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)

    def __str__(self):
        return f"Notification to {self.receiver.username} - {self.message[:20]}"

class Batch(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    required_events=models.PositiveIntegerField(unique=True,default=0)
    image=models.ImageField(upload_to='batch_images/',null=True,blank=True)
    
    def __str__(self):
        return f"{self.name} needs (≥{self.event_threshold} events)"

class UserBatch(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    batch=models.ForeignKey(Batch,on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user','batch')
    
    def __str__(self):
        return f"{self.user.username} earned {self.batch.name}"

class UserConnection(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followings"
    )

    def __str__(self):
        return f"{self.follower} following {self.following}"

    class Meta:
        constraints = [
            # 🚫 Prevent self-follow
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="prevent_self_follow"
            ),
            # 🚫 Prevent duplicate follow
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow"
            )
        ]