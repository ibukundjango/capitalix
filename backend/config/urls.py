"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Public pages
    path("", core_views.HomeView.as_view(), name="home"),
    path("about/", core_views.AboutView.as_view(), name="about"),
    path("personal/", core_views.PersonalView.as_view(), name="personal"),
    path("business/", core_views.BusinessView.as_view(), name="business"),
    path("loans/", core_views.LoansView.as_view(), name="loans"),
    path("credit-cards/", core_views.CreditCardsView.as_view(), name="credit-cards"),
    path("rates/", core_views.RatesView.as_view(), name="rates"),
    path("online-banking/", core_views.OnlineBankingView.as_view(), name="online-banking"),
    path("security/", core_views.SecurityView.as_view(), name="security"),
    path("faq/", core_views.FAQView.as_view(), name="faq"),
    path("contact/", core_views.ContactView.as_view(), name="contact"),
    path("resources/", core_views.ResourcesView.as_view(), name="resources"),

    # Public open-account page
    path("open-account/", core_views.OpenAccountView.as_view(), name="open_account_public"),

    # Accounts app
    path("accounts/", include("accounts.urls")),
    path('transactions/', include('transactions.urls')),
    path('cards/', include('cards.urls')),
    path('my-loans/', include('loans.urls')),
    path('support/', include('support.urls')),
    path('notifications/', include('notifications.urls')),
    path('staff/', include('staff.urls')),
]
