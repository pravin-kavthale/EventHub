from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        navbar_notifications = Notification.objects.filter(
            receiver=request.user
        ).order_by('-timestamp')[:5]  # latest 5 notifications

        navbar_unread_count = Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
    else:
        navbar_notifications = []
        navbar_unread_count = 0

    return {
        'navbar_notifications': navbar_notifications,
        'navbar_unread_count': navbar_unread_count
    }
