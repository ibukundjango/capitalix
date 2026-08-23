from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def notification_mark_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    return redirect('notification_list')

@login_required
def notification_mark_all_read(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return redirect('notification_list')