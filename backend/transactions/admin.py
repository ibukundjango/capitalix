from django.contrib import admin
from .models import Payee, BillPayment

@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'account_number', 'bank_name', 'created_at']
    search_fields = ['user__username', 'name', 'account_number']

@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'payee', 'amount', 'status', 'scheduled_at', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username', 'payee__name', 'reference']