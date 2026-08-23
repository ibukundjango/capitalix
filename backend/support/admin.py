from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'status', 'created_at', 'updated_at']
    list_filter = ['status']
    search_fields = ['user__username', 'user__email', 'subject', 'message']
    list_editable = ['status']

from .models import SupportTicket, SupportChatSession, SupportChatMessage

@admin.register(SupportChatSession)
class SupportChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']

@admin.register(SupportChatMessage)
class SupportChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender', 'message', 'created_at']
    list_filter = ['sender']
    search_fields = ['message']