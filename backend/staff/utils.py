from .models import AuditLog

def log_action(request, action, target=''):
    ip = request.META.get('REMOTE_ADDR')
    AuditLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        action=action,
        target=target,
        ip_address=ip
    )