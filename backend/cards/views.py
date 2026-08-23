import datetime
import random

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.views import kyc_required
from banking.models import Card
from core.email_utils import send_template_email
from notifications.utils import notify_user

from .forms import CardActionForm, CardRequestForm


@kyc_required
def card_list(request):
    """
    Display the customer's most recent card on the
    Manage Card page.
    """

    card = (
        Card.objects
        .filter(customer=request.user)
        .order_by("-id")
        .first()
    )

    # If the customer has no card yet, send them
    # to the card request page.
    if not card:
        messages.info(
            request,
            "You don't have a card yet. Please request one first.",
        )
        return redirect("card_request")

    return render(
        request,
        "cards/card_list.html",
        {
            "card": card,
            "form": CardActionForm(),
        },
    )


@kyc_required
def card_request(request):
    """
    Handle a new card request.
    """

    if request.method == "POST":
        form = CardRequestForm(request.POST)

        if form.is_valid():
            card_type = form.cleaned_data["card_type"]

            # Simulated card issuance.
            # In production, card creation/issuance should
            # be handled by your card provider.
            last_four = str(random.randint(1000, 9999))

            expiration = (
                datetime.date.today()
                + datetime.timedelta(days=3 * 365)
            )

            Card.objects.create(
                customer=request.user,
                card_type=card_type,
                last_four=last_four,
                status="active",
                expiration_date=expiration,
            )

            messages.success(
                request,
                "Card request submitted. A new card will be issued.",
            )

            return redirect("card_list")

    else:
        form = CardRequestForm()

    return render(
        request,
        "cards/card_request.html",
        {
            "form": form,
        },
    )


@kyc_required
def card_action(request, card_id):
    """
    Perform an action on a specific card belonging
    to the currently authenticated customer.
    """

    # Only allow the logged-in customer to access
    # and modify their own card.
    card = get_object_or_404(
        Card,
        id=card_id,
        customer=request.user,
    )

    if request.method == "POST":
        form = CardActionForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data["action"]

            if action == "freeze":
                card.status = "frozen"
                success_message = (
                    f"Card ending in {card.last_four} has been frozen."
                )

            elif action == "unfreeze":
                card.status = "active"
                success_message = (
                    f"Card ending in {card.last_four} has been unfrozen."
                )

            elif action == "report":
                card.status = "reported"
                success_message = (
                    f"Card ending in {card.last_four} has been reported."
                )

            elif action == "replace":
                card.status = "replaced"
                success_message = (
                    f"Replacement requested for card "
                    f"ending in {card.last_four}."
                )

            else:
                messages.error(
                    request,
                    "Invalid card action.",
                )
                return redirect("card_list")

            # Save the new card status.
            card.save(update_fields=["status"])

            # Show success message.
            messages.success(
                request,
                success_message,
            )

            # Send in-app notification.
            notify_user(
                request.user,
                "Card Action",
                success_message,
            )

            # Send email notification.
            send_template_email(
                request.user.email,
                "Card Action",
                "card_alert.html",
                {
                    "user": request.user,
                    "last_four": card.last_four,
                    "action": action,
                    "card": card,
                },
            )

            return redirect("card_list")

    else:
        form = CardActionForm()

    # IMPORTANT:
    # Your uploaded card_list.html is the Manage Card
    # template and expects "card" and "form".
    return render(
        request,
        "cards/card_list.html",
        {
            "card": card,
            "form": form,
        },
    )
