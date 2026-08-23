from django import forms
from banking.models import Loan

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['loan_type', 'amount', 'term_months']
        widgets = {
            'loan_type': forms.Select(choices=[('personal', 'Personal'), ('business', 'Business'), ('auto', 'Auto'), ('mortgage', 'Mortgage')]),
        }