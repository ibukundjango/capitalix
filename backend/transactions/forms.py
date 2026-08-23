from django import forms
from django.contrib.auth.models import User
from banking.models import BankAccount
from transactions.models import Payee, BillPayment

class TransactionFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + [
            ('deposit', 'Deposit'),
            ('withdrawal', 'Withdrawal'),
            ('transfer_in', 'Transfer In'),
            ('transfer_out', 'Transfer Out'),
            ('payment', 'Payment'),
            ('fee', 'Fee'),
            ('interest', 'Interest'),
        ]
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + [
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('reversed', 'Reversed'),
        ]
    )
    description = forms.CharField(required=False, max_length=100)

class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        empty_label="Select Account",
        required=True,
        label="From Account"
    )

    recipient_name = forms.CharField(
        max_length=100,
        required=True,
        label="Recipient Name"
    )

    recipient_account_number = forms.CharField(
        max_length=20,
        required=True,
        label="Recipient Account Number"
    )

    recipient_routing_number = forms.CharField(
        max_length=20,
        required=True,
        label="Recipient Routing Number"
    )

    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        required=True,
        label="Amount"
    )

    reference = forms.CharField(
        max_length=100,
        required=False,
        label="Reference",
        help_text="Optional note for this transfer"
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_account'].queryset = BankAccount.objects.filter(
            customer=user,
            status='active'
        )

    def clean(self):
        cleaned_data = super().clean()

        from_account = cleaned_data.get('from_account')
        recipient_account_number = cleaned_data.get('recipient_account_number')
        amount = cleaned_data.get('amount')

        # Check available balance
        if from_account and amount:
            if from_account.available_balance < amount:
                raise forms.ValidationError(
                    "Insufficient available balance."
                )

        # Prevent transfer to the same account if recipient is internal
        if from_account and recipient_account_number:
            try:
                recipient = BankAccount.objects.get(
                    account_number=recipient_account_number,
                    status='active'
                )
                if recipient.pk == from_account.pk:
                    raise forms.ValidationError(
                        "Cannot transfer money to the same account."
                    )
            except BankAccount.DoesNotExist:
                # External account — allowed
                pass

        return cleaned_data
    
from banking.models import BankAccount
from django import forms

class StatementForm(forms.Form):
    account = forms.ModelChoiceField(
        queryset=BankAccount.objects.none(),
        empty_label="Select Account",
        required=True
    )
    month = forms.ChoiceField(
        choices=[(str(i), f"{i:02d}") for i in range(1, 13)],
        required=True
    )
    year = forms.ChoiceField(
        choices=[(str(y), str(y)) for y in range(2020, 2031)],
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = BankAccount.objects.filter(
            customer=user,
            status='active'
        )

class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['name', 'account_number', 'bank_name']

class BillPaymentForm(forms.Form):
    payee = forms.ModelChoiceField(queryset=Payee.objects.none(), empty_label="Select Payee")
    amount = forms.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    reference = forms.CharField(max_length=100, required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payee'].queryset = Payee.objects.filter(user=user)

# transactions/forms.py (add this class)

class TransactionPinForm(forms.Form):
    transaction_pin = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': '••••', 'inputmode': 'numeric'}),
        label='Transaction PIN',
        help_text='Enter your 4‑digit transaction PIN.',
        required=True
    )
