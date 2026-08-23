from django.contrib import admin
from .models import StaffProfile, AuditLog

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff']
    search_fields = ['user__username', 'user__email']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'target', 'ip_address', 'timestamp']
    search_fields = ['actor__username', 'action', 'target']
    readonly_fields = ['timestamp']