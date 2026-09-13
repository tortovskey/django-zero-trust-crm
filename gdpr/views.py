from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.rbac import ADMIN, AUDITOR, USER, get_role, require_roles
from security.models import TrustedDevice
from security.services import log_security_event
from tickets.models import Ticket

from .forms import DataDeletionRequestForm, DataDeletionReviewForm
from .models import DataDeletionRequest


@require_roles(ADMIN, AUDITOR, USER)
def gdpr_home(request):
    deletion_requests = DataDeletionRequest.objects.visible_for(request.user)[:10]
    return render(request, 'gdpr/gdpr_home.html', {'deletion_requests': deletion_requests})


@require_roles(ADMIN, AUDITOR, USER)
def export_my_data(request):
    user = request.user
    profile = user.profile
    tickets = Ticket.objects.filter(requester=user).values(
        'number',
        'subject',
        'description',
        'status',
        'priority',
        'created_at',
        'updated_at',
    )
    deletion_requests = DataDeletionRequest.objects.filter(user=user).values(
        'reason',
        'status',
        'requested_at',
        'admin_comment',
    )
    devices = TrustedDevice.objects.filter(user=user).values(
        'name',
        'ip_address',
        'first_seen_at',
        'last_seen_at',
        'is_trusted',
    )
    payload = {
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'profile': {
            'role': profile.get_role_display(),
            'department': profile.department,
            'phone': profile.phone,
            'mfa_enabled': profile.mfa_enabled,
            'created_at': profile.created_at,
            'last_login_at': profile.last_login_at,
        },
        'tickets': list(tickets),
        'data_deletion_requests': list(deletion_requests),
        'trusted_devices': list(devices),
    }
    log_security_event(
        request=request,
        event_type='data_export',
        description='Экспорт персональных данных пользователя в JSON',
        risk_level='medium',
    )
    response = JsonResponse(payload, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="kosty-data-{user.username}.json"'
    return response


@require_roles(ADMIN, AUDITOR, USER)
def deletion_request_list(request):
    requests = DataDeletionRequest.objects.visible_for(request.user).select_related('user', 'client')
    return render(request, 'gdpr/deletion_request_list.html', {'deletion_requests': requests})


@require_roles(ADMIN, AUDITOR, USER)
def deletion_request_create(request):
    form = DataDeletionRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deletion_request = form.save(commit=False)
        deletion_request.user = request.user
        deletion_request.save()
        log_security_event(
            request=request,
            event_type='data_deletion_request',
            description='Создан запрос на удаление персональных данных',
            risk_level='medium',
        )
        messages.success(request, 'Запрос на удаление данных отправлен.')
        return redirect('gdpr:deletion_requests')
    return render(request, 'gdpr/deletion_request_form.html', {'form': form, 'title': 'Новый запрос'})


@require_roles(ADMIN)
def deletion_request_update(request, pk):
    deletion_request = get_object_or_404(DataDeletionRequest, pk=pk)
    form = DataDeletionReviewForm(request.POST or None, instance=deletion_request)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Статус GDPR-запроса обновлен.')
        return redirect('gdpr:deletion_requests')
    return render(request, 'gdpr/deletion_request_form.html', {'form': form, 'title': 'Рассмотрение запроса'})


def data_policy(request):
    return render(request, 'gdpr/data_policy.html')
