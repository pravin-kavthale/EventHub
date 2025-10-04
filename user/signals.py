
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from Event.models import Event
from .models import Batch,UserBatch

@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save,sender=User)
def save_profile(sender,instance,**kwargs):
    instance.profile.save()

@receiver(post_save, sender=Event)
def assign_batch_on_event(sender, instance, created, **kwargs):
    if created:
        user = instance.organizer
        event_count = Event.objects.filter(organizer=user).count()
        eligible_batches = Batch.objects.filter(required_events__lte=event_count)
        for batch in eligible_batches:
            UserBatch.objects.get_or_create(user=user, batch=batch)