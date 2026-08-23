from django.views.generic import TemplateView
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "pages/home.html"

class AboutView(TemplateView):
    template_name = "pages/about.html"

class PersonalView(TemplateView):
    template_name = "pages/personal.html"

class BusinessView(TemplateView):
    template_name = "pages/business.html"

class LoansView(TemplateView):
    template_name = "pages/loans.html"

class CreditCardsView(TemplateView):
    template_name = "pages/credit-card.html"

class RatesView(TemplateView):
    template_name = "pages/rates.html"

class OnlineBankingView(TemplateView):
    template_name = "pages/online-banking.html"

class SecurityView(TemplateView):
    template_name = "pages/security.html"

class FAQView(TemplateView):
    template_name = "pages/faq.html"

class ContactView(TemplateView):
    template_name = "pages/contact.html"

class ResourcesView(TemplateView):
    template_name = "pages/resources.html"

class OpenAccountView(TemplateView):
    template_name = "auth/open-account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["step"] = 1
        return context