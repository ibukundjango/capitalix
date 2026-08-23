from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'read', 'created_at']
    list_filter = ['read']
    search_fields = ['user__username', 'user__email', 'title', 'message']