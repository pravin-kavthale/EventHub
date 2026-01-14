from Event.models import Event,EventRegistration
from django import template

register = template.Library()

@register.simple_tag
def is_event_registered(user,event):
    if not user.is_authenticated:
        return False
    return EventRegistration.objects.filter(user=user,event=event).exists()

