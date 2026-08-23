from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary_storage.storage import MediaCloudinaryStorage

class AccountProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_profile')
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, blank=True)
    account_type = models.CharField(max_length=50, blank=True)  # Checking, Savings, etc.
    transaction_pin = models.CharField(max_length=128, blank=True)  # hashed
    email_verified = models.BooleanField(default=False)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ('NOT_STARTED', 'Not Started'),
            ('IN_PROGRESS', 'In Progress'),
            ('SUBMITTED', 'Submitted'),
            ('UNDER_REVIEW', 'Under Review'),
            ('VERIFIED', 'Verified'),
            ('REJECTED', 'Rejected'),
        ],
        default='NOT_STARTED'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class KYCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc_profile')
    title = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    government_id = models.CharField(max_length=100, blank=True)  # SSN/NIN etc.
    employment_type = models.CharField(max_length=100, blank=True)
    annual_income_range = models.CharField(max_length=100, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f"KYC for {self.user.username}"

class NextOfKin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='next_of_kin')
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    relationship = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)

class IdentityDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identity_documents')
    doc_type = models.CharField(max_length=50, choices=[
        ('PASSPORT', 'International Passport'),
        ('NATIONAL_ID', 'National ID'),
        ('DRIVERS_LICENSE', 'Driver\'s License'),
    ])
    front_image = models.ImageField(upload_to='kyc_docs/', storage=MediaCloudinaryStorage(), blank=True)
    back_image = models.ImageField(upload_to='kyc_docs/', storage=MediaCloudinaryStorage(), blank=True)
    passport_photo = models.ImageField(upload_to='kyc_docs/', storage=MediaCloudinaryStorage(), blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

# Auto-create AccountProfile when User is created
@receiver(post_save, sender=User)
def create_account_profile(sender, instance, created, **kwargs):
    if created:
        AccountProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_account_profile(sender, instance, **kwargs):
    instance.account_profile.save()