from .models import Event,EventRegistration
from django.contrib.auth.models import User


def get_event_participants(event):
    return User.objects.filter(event_registrations__event=event)