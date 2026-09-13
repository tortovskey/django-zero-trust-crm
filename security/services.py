from django.utils.text import Truncator

from .models import SecurityEvent, TrustedDevice


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR') if request else ''
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') if request else None


def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '') if request else ''


def log_security_event(request=None, user=None, event_type='access_denied', description='', risk_level='low'):
    actor = user
    if actor is None and request is not None and request.user.is_authenticated:
        actor = request.user
    return SecurityEvent.objects.create(
        user=actor,
        event_type=event_type,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        description=description,
        risk_level=risk_level,
    )


def remember_trusted_device(request, user):
    user_agent = get_user_agent(request)
    ip_address = get_client_ip(request)
    name = Truncator(user_agent or 'Unknown device').chars(80)
    device, _ = TrustedDevice.objects.get_or_create(
        user=user,
        user_agent=user_agent,
        ip_address=ip_address,
        defaults={'name': name, 'is_trusted': False},
    )
    if not device.name:
        device.name = name
    device.save()
    return device
