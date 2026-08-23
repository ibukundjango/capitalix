from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from banking.models import BankAccount, Transaction, Transfer, Loan, Card
from support.models import SupportTicket
from notifications.models import Notification
from .models import AuditLog

def is_staff(user):
    return user.is_staff or hasattr(user, 'staff_profile')

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    # Statistics
    total_customers = User.objects.filter(is_staff=False).count()
    total_accounts = BankAccount.objects.count()
    total_transactions = Transaction.objects.count()
    pending_loans = Loan.objects.filter(status='pending').count()
    open_tickets = SupportTicket.objects.filter(status='open').count()

    # Recent activity
    recent_audit_logs = AuditLog.objects.order_by('-timestamp')[:20]
    recent_transactions = Transaction.objects.order_by('-created_at')[:10]

    context = {
        'total_customers': total_customers,
        'total_accounts': total_accounts,
        'total_transactions': total_transactions,
        'pending_loans': pending_loans,
        'open_tickets': open_tickets,
        'recent_audit_logs': recent_audit_logs,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'staff/dashboard.html', context)