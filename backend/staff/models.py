from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('BANKING_ADMIN', 'Banking Admin'),
        ('CUSTOMER_SUPPORT', 'Customer Support'),
        ('LOAN_OFFICER', 'Loan Officer'),
        ('FINANCE', 'Finance'),
        ('COMPLIANCE', 'Compliance'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='CUSTOMER_SUPPORT')
    is_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=200)
    target = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} - {self.action} - {self.timestamp}"