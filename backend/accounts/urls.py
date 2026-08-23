from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "password-change/",
        views.password_change_view,
        name="password_reset"
    ),

    path(
        "verify-email/",
        views.verify_email_view,
        name="verify_email"
    ),

    path(
        "resend-verification/",
        views.resend_verification,
        name="resend_verification"
    ),

    path(
        "kyc/",
        views.kyc_submit_view,
        name="kyc_submit"
    ),

    path("accounts/", views.account_list, name="account_list"),
    path("accounts/<int:pk>/", views.account_detail, name="account_detail"),
]