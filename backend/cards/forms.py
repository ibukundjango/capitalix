from django import forms

class CardRequestForm(forms.Form):
    card_type = forms.ChoiceField(choices=[('debit', 'Debit Card'), ('credit', 'Credit Card')])
    reason = forms.CharField(widget=forms.Textarea, required=False)

class CardActionForm(forms.Form):
    action = forms.ChoiceField(choices=[('freeze', 'Freeze'), ('unfreeze', 'Unfreeze'), ('report', 'Report Lost'), ('replace', 'Request Replacement')])