from django.contrib import admin
from django.utils.html import format_html
from core.email_utils import send_template_email

from .models import (
    AccountProfile,
    KYCProfile,
    NextOfKin,
    IdentityDocument,
    EmailVerification,
)


# ============================================================
# ACCOUNT PROFILE
# ============================================================

@admin.register(AccountProfile)
class AccountProfileAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'kyc_status',
        'email_verified',
        'account_type',
        'currency',
        'created_at',
    ]

    # Allows KYC status to be changed directly
    # from the Account Profiles list.
    list_editable = [
        'kyc_status',
    ]

    list_filter = [
        'kyc_status',
        'email_verified',
        'account_type',
        'currency',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'phone',
    ]

    readonly_fields = [
        'created_at',
    ]

    actions = [
        'approve_kyc',
        'reject_kyc',
        'mark_kyc_under_review',
        'mark_kyc_submitted',
        'mark_kyc_in_progress',
        'reset_kyc',
    ]

    # ========================================================
    # KYC ACTIONS
    # ========================================================

    @admin.action(description='Approve selected users')
    def approve_kyc(self, request, queryset):
        updated = 0
    
        for profile in queryset:
            profile.kyc_status = 'VERIFIED'
            profile.save()
    
            # Send KYC approval email to this user
            try:
                send_template_email(
                    profile.user.email,
                    'KYC Verified',
                    'kyc_verified.html',
                    {
                        'user': profile.user,
                        'profile': profile,
                    }
                )
            except Exception as e:
                # Don't stop the remaining approvals if email fails
                self.message_user(
                    request,
                    f'KYC verified for {profile.user.email}, but the email could not be sent: {e}',
                    level='WARNING'
                )
    
            updated += 1
    
        self.message_user(
            request,
            f'{updated} account(s) have been verified and notified.'
        )

    @admin.action(description='Reject selected users')
    def reject_kyc(self, request, queryset):

        updated = queryset.update(
            kyc_status='REJECTED'
        )

        self.message_user(
            request,
            f'{updated} account(s) have been rejected.'
        )

    @admin.action(description='Mark KYC as under review')
    def mark_kyc_under_review(self, request, queryset):

        updated = queryset.update(
            kyc_status='UNDER_REVIEW'
        )

        self.message_user(
            request,
            f'{updated} account(s) are now under review.'
        )

    @admin.action(description='Mark KYC as submitted')
    def mark_kyc_submitted(self, request, queryset):

        updated = queryset.update(
            kyc_status='SUBMITTED'
        )

        self.message_user(
            request,
            f'{updated} account(s) have been marked as submitted.'
        )

    @admin.action(description='Mark KYC as in progress')
    def mark_kyc_in_progress(self, request, queryset):

        updated = queryset.update(
            kyc_status='IN_PROGRESS'
        )

        self.message_user(
            request,
            f'{updated} account(s) are now in progress.'
        )

    @admin.action(description='Reset KYC status')
    def reset_kyc(self, request, queryset):

        updated = queryset.update(
            kyc_status='NOT_STARTED'
        )

        self.message_user(
            request,
            f'{updated} account(s) have been reset.'
        )


# ============================================================
# KYC PROFILE
# ============================================================

@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'title',
        'gender',
        'date_of_birth',
        'nationality',
        'submitted_at',
        'reviewed_at',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'government_id',
        'nationality',
    ]

    list_filter = [
        'gender',
        'employment_type',
        'nationality',
    ]

    readonly_fields = [
        'submitted_at',
        'reviewed_at',
    ]


# ============================================================
# NEXT OF KIN
# ============================================================

@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'full_name',
        'relationship',
        'age',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'full_name',
        'relationship',
    ]

    list_filter = [
        'relationship',
    ]


# ============================================================
# IDENTITY DOCUMENTS
# ============================================================

@admin.register(IdentityDocument)
class IdentityDocumentAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'doc_type',
        'verified',
        'uploaded_at',
        'front_preview',
        'back_preview',
        'passport_preview',
    ]

    list_filter = [
        'doc_type',
        'verified',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
    ]

    readonly_fields = [
        'uploaded_at',
        'front_image_preview',
        'back_image_preview',
        'passport_photo_preview',
    ]

    fields = [
        'user',
        'doc_type',
        'front_image',
        'front_image_preview',
        'back_image',
        'back_image_preview',
        'passport_photo',
        'passport_photo_preview',
        'verified',
        'uploaded_at',
    ]

    def front_image_preview(self, obj):

        if obj.front_image:
            return format_html(
                '<img src="{}" width="180" '
                'style="border-radius:8px;" />',
                obj.front_image.url
            )

        return 'No front image'

    front_image_preview.short_description = 'Front Image Preview'

    def back_image_preview(self, obj):

        if obj.back_image:
            return format_html(
                '<img src="{}" width="180" '
                'style="border-radius:8px;" />',
                obj.back_image.url
            )

        return 'No back image'

    back_image_preview.short_description = 'Back Image Preview'

    def passport_photo_preview(self, obj):

        if obj.passport_photo:
            return format_html(
                '<img src="{}" width="180" '
                'style="border-radius:8px;" />',
                obj.passport_photo.url
            )

        return 'No passport photo'

    passport_photo_preview.short_description = (
        'Passport Photo Preview'
    )

    def front_preview(self, obj):

        if obj.front_image:
            return format_html(
                '<img src="{}" width="70" '
                'style="border-radius:5px;" />',
                obj.front_image.url
            )

        return '-'

    front_preview.short_description = 'Front'

    def back_preview(self, obj):

        if obj.back_image:
            return format_html(
                '<img src="{}" width="70" '
                'style="border-radius:5px;" />',
                obj.back_image.url
            )

        return '-'

    back_preview.short_description = 'Back'

    def passport_preview(self, obj):

        if obj.passport_photo:
            return format_html(
                '<img src="{}" width="70" '
                'style="border-radius:5px;" />',
                obj.passport_photo.url
            )

        return '-'

    passport_preview.short_description = 'Photo'


# ============================================================
# EMAIL VERIFICATION
# ============================================================

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'code',
        'created_at',
        'expires_at',
        'verified',
        'attempts',
    ]

    list_filter = [
        'verified',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'code',
    ]

    readonly_fields = [
        'created_at',
    ]
