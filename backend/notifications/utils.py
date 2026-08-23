from .models import Notification

def notify_user(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)