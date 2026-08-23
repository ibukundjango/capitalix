from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SupportTicket
from .forms import SupportTicketForm

@login_required
def ticket_list(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Support ticket submitted.')
            return redirect('ticket_list')
    else:
        form = SupportTicketForm()
    return render(request, 'support/ticket_create.html', {'form': form})

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    return render(request, 'support/ticket_detail.html', {'ticket': ticket})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import SupportTicket, SupportChatSession, SupportChatMessage
from notifications.utils import notify_user

@csrf_exempt
@require_POST
def chat_send_message(request):
    data = json.loads(request.body)
    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    # Get or create session
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        chat_session, created = SupportChatSession.objects.get_or_create(
            user=request.user,
            session_key=session_key if not request.user else ''
        )
    else:
        chat_session, created = SupportChatSession.objects.get_or_create(
            session_key=session_key
        )

    # Save user message
    SupportChatMessage.objects.create(
        session=chat_session,
        sender='user',
        message=user_message
    )

    # Bot response
    bot_response = (
        "Thanks for providing those details. This type of request needs to be reviewed by our support team. "
        "You can send this conversation to our customer service team by email, and an agent will review it promptly."
    )
    SupportChatMessage.objects.create(
        session=chat_session,
        sender='bot',
        message=bot_response
    )

    return JsonResponse({
        'bot_response': bot_response,
        'session_id': chat_session.id,
    })

@csrf_exempt
@require_POST
def chat_send_email(request):
    data = json.loads(request.body)
    session_id = data.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session not found'}, status=400)

    chat_session = SupportChatSession.objects.get(id=session_id)
    messages = chat_session.messages.order_by('created_at')

    # Build conversation text
    conversation = ""
    for msg in messages:
        sender = "Customer" if msg.sender == 'user' else "Support Bot"
        conversation += f"{sender}: {msg.message}\n"

    # Create support ticket
    ticket = SupportTicket.objects.create(
        user=chat_session.user if chat_session.user else None,
        subject="Chat Support Request",
        message=conversation,
        status='open'
    )

    # Send email to support
    send_mail(
        subject=f"New Chat Support Request #{ticket.id}",
        message=f"Conversation:\n\n{conversation}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.DEFAULT_FROM_EMAIL],  # or support email
    )

    # Notify user if logged in
    if chat_session.user:
        notify_user(
            chat_session.user,
            "Support Request Sent",
            "Your support request has been sent to our team."
        )

    return JsonResponse({'success': True, 'ticket_id': ticket.id})