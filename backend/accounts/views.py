from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import (
    RegistrationStep1Form, RegistrationStep2Form, RegistrationStep3Form, RegistrationStep4Form,
    EmailVerificationForm, KYCProfileForm, NextOfKinForm, IdentityDocumentForm, KYCTermsForm,
    LoginForm, AccountProfileForm
)
from django.contrib.auth.models import User
from .models import AccountProfile, KYCProfile, NextOfKin, IdentityDocument, EmailVerification
from django.core.mail import send_mail
import random
import hashlib
from django.db.models import Sum
from banking.models import BankAccount, Transaction
from notifications.utils import notify_user
from core.email_utils import send_template_email
from django.core.cache import cache
import time


# ----------------------------------------------------------
# AUTH HELPERS
# ----------------------------------------------------------

def redirect_after_login(user):
    profile = user.account_profile
    if not profile.email_verified:
        return redirect('verify_email')
    return redirect('dashboard')

def fully_verified_required(view_func):
    """Decorator to require email verified and KYC verified."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = request.user.account_profile
        if not profile.email_verified:
            return redirect('verify_email')
        if profile.kyc_status != 'VERIFIED':
            return redirect('kyc_submit')
        return view_func(request, *args, **kwargs)
    return wrapper


# ----------------------------------------------------------
# RATE LIMIT HELPERS
# ----------------------------------------------------------

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_rate_limit(key, max_attempts=5, timeout=900):
    attempts = cache.get(key, 0)
    return attempts < max_attempts

def increment_rate_limit(key, timeout=900):
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout)


# ----------------------------------------------------------
# REGISTRATION (with Back Button Support)
# ----------------------------------------------------------

def register_view(request):
    """
    Multi-step account registration.

    Step 1: Personal information
    Step 2: Contact information
    Step 3: Account setup
    Step 4: Password/security and account creation

    Supports:
    - 'back' parameter to go back a step
    - Full country dropdown via form
    - PIN validation (4 digits, numeric, not sequential)
    - Password validation (min 8 chars, upper, lower, digit, special)
    """

    if request.method == "POST":
        step = request.POST.get("step", "1")
        # 👇 NEW: Check for "back" button
        if request.POST.get("back"):
            try:
                current_step = int(step)
                if current_step > 1:
                    return redirect(reverse("register") + f"?step={current_step - 1}")
                return redirect(reverse("register") + "?step=1")
            except (TypeError, ValueError):
                return redirect(reverse("register") + "?step=1")
    else:
        step = request.GET.get("step", "1")

    try:
        step = int(step)
    except (TypeError, ValueError):
        step = 1

    if step not in [1, 2, 3, 4]:
        step = 1

    account_type = request.GET.get("account_type")

    if step == 1:
        request.session.pop("reg_data", None)

    reg_data = request.session.get("reg_data", {})
    reg_data = dict(reg_data)

    valid_account_types = {
        "checking", "savings", "money_market",
        "certificate", "business", "investment"
    }

    if account_type in valid_account_types:
        reg_data["account_type"] = account_type
        request.session["reg_data"] = reg_data
        request.session.modified = True

    # ------------------------------------------------
    # POST REQUEST
    # ------------------------------------------------
    if request.method == "POST":

        if step == 1:
            form = RegistrationStep1Form(request.POST)
            if form.is_valid():
                reg_data.update(form.cleaned_data)
                request.session["reg_data"] = reg_data
                request.session.modified = True
                return redirect(reverse("register") + "?step=2")

        elif step == 2:
            form = RegistrationStep2Form(request.POST)
            if form.is_valid():
                reg_data.update(form.cleaned_data)

                selected_account_type = (
                    request.POST.get("account_type")
                    or request.GET.get("account_type")
                    or reg_data.get("account_type")
                )
                if selected_account_type in valid_account_types:
                    reg_data["account_type"] = selected_account_type

                request.session["reg_data"] = reg_data
                request.session.modified = True
                return redirect(reverse("register") + "?step=3")

        elif step == 3:
            form = RegistrationStep3Form(
                request.POST,
                initial={"account_type": reg_data.get("account_type", "")}
            )
            if form.is_valid():
                reg_data.update(form.cleaned_data)
                request.session["reg_data"] = reg_data
                request.session.modified = True
                return redirect(reverse("register") + "?step=4")

        elif step == 4:
            form = RegistrationStep4Form(request.POST)
            if form.is_valid():
                required_previous_fields = [
                    "first_name", "last_name", "username",
                    "email", "phone", "country", "currency",
                    "account_type", "transaction_pin"
                ]
                missing_fields = [
                    field for field in required_previous_fields
                    if not reg_data.get(field)
                ]
                if missing_fields:
                    messages.error(
                        request,
                        "Your registration session is incomplete. "
                        "Please restart the registration process."
                    )
                    request.session.pop("reg_data", None)
                    return redirect(reverse("register") + "?step=1")

                username = reg_data["username"]
                if User.objects.filter(username=username).exists():
                    messages.error(request, "That username is already registered.")
                    return redirect(reverse("register") + "?step=1")

                email = reg_data["email"]
                if User.objects.filter(email=email).exists():
                    messages.error(request, "That email is already registered.")
                    return redirect(reverse("register") + "?step=2")

                user = User.objects.create_user(
                    username=reg_data["username"],
                    email=reg_data["email"],
                    password=form.cleaned_data["password"],
                    first_name=reg_data["first_name"],
                    last_name=reg_data["last_name"],
                )

                profile = user.account_profile
                profile.phone = reg_data["phone"]
                profile.country = reg_data["country"]
                profile.currency = reg_data["currency"]
                profile.account_type = reg_data["account_type"]

                pin_hash = hashlib.sha256(
                    reg_data["transaction_pin"].encode("utf-8")
                ).hexdigest()
                profile.transaction_pin = pin_hash
                profile.email_verified = False
                profile.kyc_status = "NOT_STARTED"
                profile.save()

                notify_user(
                    user,
                    "Welcome to Capitalix",
                    "Your account has been created. Please verify your email address."
                )

                send_template_email(
                    user.email,
                    'Welcome to Capitalix',
                    'welcome.html',
                    {'user': user}
                )

                request.session.pop("reg_data", None)
                request.session.modified = True

                try:
                    send_verification_email(user)
                except Exception:
                    pass

                login(request, user)
                messages.success(
                    request,
                    "Account created successfully! Please check your email to verify your address."
                )
                return redirect("verify_email")

    else:
        if step == 1:
            form = RegistrationStep1Form()
        elif step == 2:
            form = RegistrationStep2Form(
                initial={
                    "email": reg_data.get("email", ""),
                    "phone": reg_data.get("phone", ""),
                    "country": reg_data.get("country", ""),
                }
            )
        elif step == 3:
            form = RegistrationStep3Form(
                initial={
                    "currency": reg_data.get("currency", ""),
                    "account_type": reg_data.get("account_type", ""),
                    "transaction_pin": "",  # Don't pre-fill PIN
                }
            )
        elif step == 4:
            form = RegistrationStep4Form()

    # 👇 Add the current step to context so the template can show progress
    return render(
        request,
        "auth/register_step.html",
        {
            "form": form,
            "step": step,
            "reg_data": reg_data,
            "account_type": reg_data.get("account_type", ""),
        },
    )


# ----------------------------------------------------------
# EMAIL VERIFICATION
# ----------------------------------------------------------

def send_verification_email(user):
    import datetime
    code = str(random.randint(100000, 999999))
    expires = timezone.now() + datetime.timedelta(minutes=60)
    EmailVerification.objects.create(user=user, code=code, expires_at=expires)

    send_template_email(
        user.email,
        'Capitalix - Verify your email',
        'verify_email.html',
        {'user': user, 'code': code}
    )


@login_required
def verify_email_view(request):
    if request.method == 'POST':
        ip = get_client_ip(request)
        rate_key = f'email_verify_{ip}_{request.user.id}'

        if not check_rate_limit(rate_key, max_attempts=5, timeout=900):
            messages.error(
                request,
                "Too many verification attempts. Please try again in 15 minutes."
            )
            return redirect('verify_email')

        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                ver_record = EmailVerification.objects.filter(
                    user=request.user, verified=False
                ).latest('created_at')
            except EmailVerification.DoesNotExist:
                messages.error(request, 'No pending verification.')
                return redirect('dashboard')

            if ver_record.is_expired():
                messages.error(request, 'Code expired. Request a new one.')
                return redirect('resend_verification')

            if ver_record.code != code:
                increment_rate_limit(rate_key)
                ver_record.attempts += 1
                ver_record.save()
                messages.error(request, 'Invalid code.')
                return redirect('verify_email')

            ver_record.verified = True
            ver_record.save()
            request.user.account_profile.email_verified = True
            request.user.account_profile.save()

            notify_user(
                request.user,
                "Email Verified",
                "Your email address has been successfully verified."
            )

            messages.success(request, 'Email verified successfully!')
            return redirect('dashboard')
        else:
            increment_rate_limit(rate_key)
    else:
        form = EmailVerificationForm()

    return render(request, 'auth/verify_email.html', {'form': form})


@login_required
def resend_verification(request):
    send_verification_email(request.user)
    messages.info(request, 'A new verification code has been sent to your email.')
    return redirect('verify_email')


# ----------------------------------------------------------
# LOGIN / LOGOUT
# ----------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect_after_login(request.user)

    if request.method == 'POST':
        username = request.POST.get('username', '')
        ip = get_client_ip(request)
        rate_key = f'login_rate_{ip}_{username}'

        if not check_rate_limit(rate_key, max_attempts=5, timeout=900):
            messages.error(
                request,
                "Too many login attempts. Please try again in 15 minutes."
            )
            form = LoginForm(request=request)
            return render(request, 'auth/login.html', {'form': form})

        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Prevent session fixation
            request.session.cycle_key()

            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect_after_login(user)
        else:
            increment_rate_limit(rate_key)
            messages.error(request, "Invalid login credentials.")
    else:
        form = LoginForm(request=request)

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ----------------------------------------------------------
# PROFILE
# ----------------------------------------------------------

@fully_verified_required
def profile_view(request):
    profile_form = AccountProfileForm(instance=request.user.account_profile)
    if request.method == 'POST':
        profile_form = AccountProfileForm(request.POST, instance=request.user.account_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    return render(request, 'profile.html', {'profile_form': profile_form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'auth/password_change.html', {'form': form})


# ----------------------------------------------------------
# KYC
# ----------------------------------------------------------

def kyc_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = request.user.account_profile
        if profile.kyc_status != 'VERIFIED':
            messages.info(request, "Please complete your KYC verification to access this service.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def kyc_submit_view(request):
    if request.user.account_profile.kyc_status == 'VERIFIED':
        messages.info(request, 'Your identity is already verified.')
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('dashboard')

    kyc = KYCProfile.objects.get_or_create(user=request.user)[0]
    kyc_form = KYCProfileForm(request.POST, instance=kyc)
    next_of_kin_form = NextOfKinForm(request.POST)
    doc_form = IdentityDocumentForm(request.POST, request.FILES)
    terms_form = KYCTermsForm(request.POST)

    if all([kyc_form.is_valid(), next_of_kin_form.is_valid(),
            doc_form.is_valid(), terms_form.is_valid()]):
        kyc_form.save()
        next_of_kin = next_of_kin_form.save(commit=False)
        next_of_kin.user = request.user
        next_of_kin.save()
        identity = doc_form.save(commit=False)
        identity.user = request.user
        identity.save()
        request.user.account_profile.kyc_status = 'SUBMITTED'
        request.user.account_profile.save()

        notify_user(
            request.user,
            "KYC Submitted",
            "Your KYC application has been submitted for review."
        )

        messages.success(request, 'KYC submitted for review.')
        return redirect('dashboard')

    context = {
        'profile': request.user.account_profile,
        'bank_accounts': request.user.bank_accounts.filter(status='active'),
        'total_balance': 0,
        'available_balance': 0,
        'recent_transactions': [],
        'kyc_form': kyc_form,
        'next_of_kin_form': next_of_kin_form,
        'doc_form': doc_form,
        'terms_form': terms_form,
    }
    return render(request, 'dashboard.html', context)


# ----------------------------------------------------------
# DASHBOARD
# ----------------------------------------------------------

@login_required
def dashboard_view(request):
    profile = request.user.account_profile
    bank_accounts = request.user.bank_accounts.filter(status='active')
    total_balance = bank_accounts.aggregate(total=Sum('balance'))['total'] or 0
    available_balance = bank_accounts.aggregate(total=Sum('available_balance'))['total'] or 0
    recent_transactions = Transaction.objects.filter(
        account__in=bank_accounts
    ).order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'bank_accounts': bank_accounts,
        'total_balance': total_balance,
        'available_balance': available_balance,
        'recent_transactions': recent_transactions,
    }

    if profile.kyc_status in ['NOT_STARTED', 'IN_PROGRESS', 'REJECTED']:
        context.update(get_kyc_forms(request.user))
        try:
            kyc_profile = request.user.kyc_profile
        except KYCProfile.DoesNotExist:
            kyc_profile = None
        context['kyc_profile'] = kyc_profile

    return render(request, 'dashboard.html', context)


# ----------------------------------------------------------
# ACCOUNTS
# ----------------------------------------------------------

@fully_verified_required
def account_list(request):
    accounts = request.user.bank_accounts.filter(status='active')
    return render(request, 'accounts/account_list.html', {'accounts': accounts})


@fully_verified_required
def account_detail(request, pk):
    account = get_object_or_404(BankAccount, pk=pk, customer=request.user)
    transactions = account.transactions.order_by('-created_at')[:20]
    return render(request, 'accounts/account_detail.html', {
        'account': account,
        'transactions': transactions,
    })


# ----------------------------------------------------------
# KYC FORM HELPER
# ----------------------------------------------------------

def get_kyc_forms(user, data=None, files=None):
    kyc = KYCProfile.objects.get_or_create(user=user)[0]
    kyc_form = KYCProfileForm(data, instance=kyc)
    next_of_kin_form = NextOfKinForm(data)
    doc_form = IdentityDocumentForm(data, files)
    terms_form = KYCTermsForm(data)
    return {
        'kyc_form': kyc_form,
        'next_of_kin_form': next_of_kin_form,
        'doc_form': doc_form,
        'terms_form': terms_form,
    }