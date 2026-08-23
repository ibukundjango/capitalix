from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from accounts.views import kyc_required
from banking.models import BankAccount, Transaction, Transfer
from .models import Payee, BillPayment
from .forms import TransactionFilterForm, TransferForm, BillPaymentForm, StatementForm, TransactionPinForm
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from datetime import datetime
import calendar
from notifications.utils import notify_user
from core.email_utils import send_template_email
import hashlib
from core.email_utils import send_template_email
from notifications.utils import notify_user

@login_required
def transaction_history(request):
    user = request.user
    accounts = BankAccount.objects.filter(customer=user, status='active')
    transactions = Transaction.objects.filter(account__in=accounts).order_by('-created_at')
    form = TransactionFilterForm(request.GET)

    if form.is_valid():
        data = form.cleaned_data
        if data.get('date_from'):
            transactions = transactions.filter(created_at__date__gte=data['date_from'])
        if data.get('date_to'):
            transactions = transactions.filter(created_at__date__lte=data['date_to'])
        if data.get('transaction_type'):
            transactions = transactions.filter(transaction_type=data['transaction_type'])
        if data.get('status'):
            transactions = transactions.filter(status=data['status'])
        if data.get('description'):
            transactions = transactions.filter(description__icontains=data['description'])

    context = {
        'form': form,
        'transactions': transactions,
        'accounts': accounts,
    }
    return render(request, 'transactions/history.html', context)

@kyc_required
def transfer_view(request):
    if request.method == 'POST':
        form = TransferForm(request.user, request.POST)
        if form.is_valid():
            from_account = form.cleaned_data['from_account']
            recipient_name = form.cleaned_data['recipient_name']
            recipient_account_number = form.cleaned_data['recipient_account_number']
            recipient_routing_number = form.cleaned_data['recipient_routing_number']
            amount = form.cleaned_data['amount']
            reference = form.cleaned_data['reference']

            request.session['transfer_data'] = {
                'from_account_id': from_account.id,
                'recipient_name': recipient_name,
                'recipient_account_number': recipient_account_number,
                'recipient_routing_number': recipient_routing_number,
                'amount': str(amount),
                'reference': reference,
            }
            return redirect('transfer_review')
    else:
        form = TransferForm(request.user)

    return render(request, 'transfers/transfer_form.html', {'form': form})

@kyc_required
def transfer_review(request):
    transfer_data = request.session.get('transfer_data')
    if not transfer_data:
        messages.error(request, "No transfer in progress.")
        return redirect('transfer')

    from_account = get_object_or_404(
        BankAccount,
        id=transfer_data['from_account_id'],
        customer=request.user,
        status='active'
    )

    amount = Decimal(transfer_data['amount'])
    reference = transfer_data.get('reference', '')
    recipient_name = transfer_data.get('recipient_name', '')
    recipient_account_number = transfer_data.get('recipient_account_number', '')
    recipient_routing_number = transfer_data.get('recipient_routing_number', '')

    if request.method == 'POST':
        pin_form = TransactionPinForm(request.POST)
        if pin_form.is_valid():
            pin = pin_form.cleaned_data['transaction_pin']
            pin_hash = hashlib.sha256(pin.encode('utf-8')).hexdigest()

            if pin_hash != request.user.account_profile.transaction_pin:
                messages.error(request, "Invalid transaction PIN.")
                return redirect('transfer_review')

            try:
                with transaction.atomic():
                    # Lock the sender account
                    from_account = BankAccount.objects.select_for_update().get(
                        id=from_account.id
                    )

                    # Check balance again
                    if from_account.available_balance < amount:
                        raise ValueError("Insufficient available balance.")

                    # Debit sender
                    from_account.balance -= amount
                    from_account.available_balance -= amount
                    from_account.save()

                    # Try to find internal recipient
                    recipient_account = BankAccount.objects.select_for_update().filter(
                        account_number=recipient_account_number,
                        status='active'
                    ).first()

                    # Create sender transaction
                    Transaction.objects.create(
                        account=from_account,
                        transaction_type='transfer_out',
                        amount=-amount,
                        description=f'Transfer to {recipient_name} ({recipient_account_number})',
                        reference=reference,
                        status='completed',
                        created_at=timezone.now()
                    )

                    # If recipient is internal, credit their account
                    if recipient_account and recipient_account.pk != from_account.pk:
                        recipient_account.balance += amount
                        recipient_account.available_balance += amount
                        recipient_account.save()

                        Transaction.objects.create(
                            account=recipient_account,
                            transaction_type='transfer_in',
                            amount=amount,
                            description=f'Transfer from {from_account.account_number}',
                            reference=reference,
                            status='completed',
                            created_at=timezone.now()
                        )

                        Transfer.objects.create(
                            sender_account=from_account,
                            recipient_account=recipient_account,
                            amount=amount,
                            reference=reference,
                            status='completed',
                            created_at=timezone.now()
                        )

                # Notifications
                notify_user(
                    request.user,
                    "Transfer Completed",
                    f"Your transfer of ${amount} was successful."
                )

                if recipient_account and recipient_account.customer != request.user:
                    notify_user(
                        recipient_account.customer,
                        "Transfer Received",
                        f"You received ${amount} from {from_account.account_number}."
                    )

                # Emails
                send_template_email(
                    request.user.email,
                    'Debit Alert',
                    'transfer_debit.html',
                    {
                        'user': request.user,
                        'amount': amount,
                        'account_number': from_account.account_number,
                        'reference': reference,
                    }
                )

                if recipient_account and recipient_account.customer != request.user:
                    send_template_email(
                        recipient_account.customer.email,
                        'Credit Alert',
                        'transfer_credit.html',
                        {
                            'user': recipient_account.customer,
                            'amount': amount,
                            'account_number': recipient_account.account_number,
                            'reference': reference,
                        }
                    )

                request.session.pop('transfer_data', None)
                messages.success(request, "Transfer completed successfully.")
                return redirect('transaction_history')

            except Exception as e:
                messages.error(request, f"Transfer failed: {str(e)}")
                return redirect('transfer_view')

    else:
        pin_form = TransactionPinForm()

    return render(request, 'transfers/transfer_review.html', {
        'from_account': from_account,
        'amount': amount,
        'reference': reference,
        'recipient_name': recipient_name,
        'recipient_account_number': recipient_account_number,
        'recipient_routing_number': recipient_routing_number,
        'pin_form': pin_form,
    })


@kyc_required
def statement_form(request):
    if request.method == 'POST':
        form = StatementForm(request.user, request.POST)
        if form.is_valid():
            account = form.cleaned_data['account']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            return redirect('statement_view', account_id=account.id, year=year, month=month)
    else:
        form = StatementForm(request.user)
    return render(request, 'statements/statement_form.html', {'form': form})

@kyc_required
def statement_view(request, account_id, year, month):
    account = get_object_or_404(
        BankAccount,
        id=account_id,
        customer=request.user,
        status='active'
    )
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        return redirect('statement_form')

    # Filter transactions for that month
    transactions = Transaction.objects.filter(
        account=account,
        created_at__year=year,
        created_at__month=month
    ).order_by('created_at')

    # Calculate totals
    total_in = sum(tx.amount for tx in transactions if tx.amount > 0)
    total_out = sum(-tx.amount for tx in transactions if tx.amount < 0)

    context = {
        'account': account,
        'transactions': transactions,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'total_in': total_in,
        'total_out': total_out,
    }
    return render(request, 'statements/statement_detail.html', context)

@kyc_required
def statement_download(request, account_id, year, month):
    account = get_object_or_404(
        BankAccount,
        id=account_id,
        customer=request.user,
        status='active'
    )
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        return redirect('statement_form')

    transactions = Transaction.objects.filter(
        account=account,
        created_at__year=year,
        created_at__month=month
    ).order_by('created_at')

    total_in = sum(tx.amount for tx in transactions if tx.amount > 0)
    total_out = sum(-tx.amount for tx in transactions if tx.amount < 0)

    html_string = render_to_string('statements/statement_pdf.html', {
        'account': account,
        'transactions': transactions,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'total_in': total_in,
        'total_out': total_out,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="statement_{account.account_number}_{year}_{month}.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)

    return response

@kyc_required
def transaction_receipt(request, pk):
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        account__customer=request.user
    )
    html_string = render_to_string(
        'transactions/transaction_receipt_pdf.html',
        {'transaction': transaction}
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="receipt_{transaction.pk}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)

    return response

@kyc_required
def payee_list(request):
    payees = Payee.objects.filter(user=request.user)
    return render(request, 'billpay/payee_list.html', {'payees': payees})

@kyc_required
def payee_add(request):
    if request.method == 'POST':
        form = PayeeForm(request.POST)
        if form.is_valid():
            payee = form.save(commit=False)
            payee.user = request.user
            payee.save()
            messages.success(request, "Payee added.")
            return redirect('payee_list')
    else:
        form = PayeeForm()
    return render(request, 'billpay/payee_add.html', {'form': form})

@kyc_required
def bill_pay(request):
    if request.method == 'POST':
        form = BillPaymentForm(request.user, request.POST)
        if form.is_valid():
            payee = form.cleaned_data['payee']
            amount = form.cleaned_data['amount']
            reference = form.cleaned_data['reference']
            BillPayment.objects.create(
                user=request.user,
                payee=payee,
                amount=amount,
                reference=reference,
                status='pending',
                scheduled_at=timezone.now()
            )
            messages.success(request, "Payment scheduled.")
            return redirect('bill_payment_history')
    else:
        form = BillPaymentForm(request.user)
    return render(request, 'billpay/bill_pay.html', {'form': form})

@kyc_required
def bill_payment_history(request):
    payments = BillPayment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'billpay/bill_payment_history.html', {'payments': payments})
