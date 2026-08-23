from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.views import kyc_required
from banking.models import Loan
from .forms import LoanApplicationForm
from notifications.utils import notify_user
from core.email_utils import send_template_email

@kyc_required
def loan_list(request):
    loans = Loan.objects.filter(customer=request.user)
    return render(request, 'loans/loan_list.html', {'loans': loans})

@kyc_required
def loan_apply(request):
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.customer = request.user
            loan.interest_rate = 5.5  # demo rate
            loan.status = 'pending'
            loan.save()
            messages.success(request, "Loan application submitted. We will review it shortly.")
            notify_user(request.user, "Loan Application Submitted", "Your loan application has been received and is pending review.")
            send_template_email(
                request.user.email,
                'Loan Application Submitted',
                'loan_update.html',
                {'user': request.user, 'loan_type': loan.loan_type, 'status': 'pending', 'amount': loan.amount}
            )
            return redirect('loan_list')
    else:
        form = LoanApplicationForm()
    return render(request, 'loans/loan_apply.html', {'form': form})