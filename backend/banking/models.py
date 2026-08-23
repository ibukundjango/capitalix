from django.db import models
from django.contrib.auth.models import User
from accounts.models import AccountProfile
from django.core.validators import MinValueValidator
from decimal import Decimal

class BankAccount(models.Model):
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('fixed_deposit', 'Fixed Deposit'),
        ('current', 'Current'),
        ('business', 'Business'),
        ('investment', 'Investment'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('frozen', 'Frozen'),
        ('closed', 'Closed'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=20, unique=True)  # generated
    account_type = models.CharField(max_length=30, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.account_number} ({self.account_type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('payment', 'Payment'),
        ('fee', 'Fee'),
        ('interest', 'Interest'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]

    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    sender_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transfers_sent')
    recipient_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transfers_received')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Card(models.Model):
    CARD_TYPES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='cards', null=True, blank=True)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    last_four = models.CharField(max_length=4)  # only last 4 digits stored
    status = models.CharField(max_length=20, default='active')
    expiration_date = models.DateField()

class Loan(models.Model):
    LOAN_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

# cards/models.py (if separate app)
# transactions/models.py (if separate)
# loans/models.py (if separate)