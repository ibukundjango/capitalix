from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_template_email(
    to_email,
    subject,
    template_name,
    context=None,
    from_email=None
):
    """
    Send an HTML email using a template.
    """
    context = context or {}
    context.setdefault('user', None)
    context.setdefault('dashboard_url', settings.SITE_URL + '/accounts/dashboard/')
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    html_content = render_to_string(f'emails/{template_name}', context)
    plain_message = context.get('plain_message', '')  # optional

    msg = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def send_email_with_template(to_email, subject, template_name, context):
    send_template_email(to_email, subject, template_name, context)