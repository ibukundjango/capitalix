import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import AccountProfile
from .models import BankAccount
from notifications.utils import notify_user


def generate_account_number():
    while True:
        num = ''.join(random.choices(string.digits, k=10))
        if not BankAccount.objects.filter(account_number=num).exists():
            return num


@receiver(post_save, sender=AccountProfile)
def create_bank_account_on_kyc_verified(sender, instance, **kwargs):
    if instance.kyc_status == 'VERIFIED':
        # Only create if no active account exists
        existing_accounts = BankAccount.objects.filter(customer=instance.user, status='active')
        if existing_accounts.count() == 0:
            BankAccount.objects.create(
                customer=instance.user,
                account_number=generate_account_number(),
                account_type=instance.account_type or 'checking',
                balance=0.00,
                available_balance=0.00,
                status='active'
            )
        notify_user(instance.user, "Account Activated", "Your KYC has been verified and your bank account is now active.")