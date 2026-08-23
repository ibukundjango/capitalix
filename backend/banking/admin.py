from django.contrib import admin
from .models import BankAccount, Transaction, Transfer, Card, Loan
from notifications.utils import notify_user
from core.email_utils import send_template_email


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer',
        'account_number',
        'account_type',
        'balance',
        'available_balance',
        'status',
        'opened_at',
    ]
    list_filter = ['account_type', 'status']
    search_fields = ['account_number', 'customer__username', 'customer__email']
    readonly_fields = ['opened_at']

    def save_model(self, request, obj, form, change):
        """
        Detect when an admin increases the balance and send a credit alert.
        """
        if change and obj.pk:
            old_balance = BankAccount.objects.get(pk=obj.pk).balance
        else:
            old_balance = 0

        super().save_model(request, obj, form, change)

        if obj.balance > old_balance:
            credit_amount = obj.balance - old_balance

            notify_user(
                obj.customer,
                "Credit Alert",
                f"Your account {obj.account_number} has been credited with ${credit_amount:.2f}."
            )

            try:
                send_template_email(
                    obj.customer.email,
                    'Credit Alert',
                    'transfer_credit.html',
                    {
                        'user': obj.customer,
                        'amount': credit_amount,
                        'account_number': obj.account_number,
                    }
                )
            except Exception:
                pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status']
    search_fields = ['account__account_number', 'description', 'reference']


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['sender_account', 'recipient_account', 'amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['sender_account__account_number', 'recipient_account__account_number', 'reference']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['customer', 'card_type', 'last_four', 'status', 'expiration_date']
    list_filter = ['card_type', 'status']
    search_fields = ['customer__username', 'last_four']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['customer', 'loan_type', 'amount', 'interest_rate', 'term_months', 'status']
    list_filter = ['loan_type', 'status']
    search_fields = ['customer__username', 'loan_type']
