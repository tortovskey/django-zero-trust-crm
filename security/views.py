from django.shortcuts import render

from accounts.rbac import ADMIN, AUDITOR, SECURITY, require_roles

from .models import SecurityEvent, TrustedDevice


@require_roles(ADMIN, SECURITY, AUDITOR)
def event_list(request):
    events = SecurityEvent.objects.select_related('user')
    event_type = request.GET.get('event_type')
    risk = request.GET.get('risk')
    if event_type:
        events = events.filter(event_type=event_type)
    if risk:
        events = events.filter(risk_level=risk)
    return render(
        request,
        'security/event_list.html',
        {
            'events': events[:200],
            'event_type': event_type or '',
            'risk': risk or '',
            'event_types': SecurityEvent.EventType.choices,
            'risk_levels': SecurityEvent.RiskLevel.choices,
        },
    )


@require_roles(ADMIN, SECURITY, AUDITOR)
def device_list(request):
    devices = TrustedDevice.objects.select_related('user')
    return render(request, 'security/device_list.html', {'devices': devices})
