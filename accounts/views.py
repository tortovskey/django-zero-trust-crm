from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from clients.models import Client
from gdpr.models import DataDeletionRequest
from security.models import SecurityEvent, TrustedDevice
from security.services import log_security_event, remember_trusted_device
from tickets.models import Ticket

from .forms import ProfileForm, RegistrationForm, UserRoleForm
from .models import Profile
from .rbac import ADMIN, AUDITOR, MANAGER, SECURITY, USER, get_role, require_roles


@login_required
def dashboard(request):
    role = get_role(request.user)
    if role == USER:
        tickets = Ticket.objects.filter(requester=request.user)
        clients_count = 0
    else:
        tickets = Ticket.objects.all()
        clients_count = Client.objects.count() if role in {ADMIN, MANAGER, AUDITOR} else 0

    context = {
        'clients_count': clients_count,
        'tickets_count': tickets.count(),
        'open_tickets_count': tickets.exclude(status__in=[Ticket.Status.CLOSED, Ticket.Status.REJECTED]).count(),
        'security_events_count': SecurityEvent.objects.count() if role in {ADMIN, SECURITY, AUDITOR} else 0,
        'gdpr_requests_count': DataDeletionRequest.objects.visible_for(request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        log_security_event(
            request=request,
            user=user,
            event_type='registration',
            description='Регистрация нового пользователя',
            risk_level='low',
        )
        messages.success(request, 'Регистрация завершена. Теперь можно войти.')
        return redirect('accounts:login')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        username = request.POST.get('username', '')
        user = authenticate(request, username=username, password=request.POST.get('password', ''))
        if user is not None:
            profile = user.profile
            if not user.is_active or not profile.is_active_profile:
                log_security_event(
                    request=request,
                    user=user,
                    event_type='login_failed',
                    description='Попытка входа неактивного пользователя',
                    risk_level='medium',
                )
                messages.error(request, 'Учетная запись отключена.')
            elif profile.mfa_enabled:
                request.session['pending_mfa_user_id'] = user.id
                messages.info(request, 'Введите демонстрационный MFA-код 123456.')
                return redirect('accounts:mfa')
            else:
                _finish_login(request, user)
                return redirect('dashboard')
        else:
            log_security_event(
                request=request,
                event_type='login_failed',
                description=f'Неуспешная попытка входа для логина {username}',
                risk_level='medium',
            )
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'accounts/login.html', {'form': form})


def mfa_view(request):
    user_id = request.session.get('pending_mfa_user_id')
    if not user_id:
        return redirect('accounts:login')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if request.POST.get('code') == '123456':
            request.session.pop('pending_mfa_user_id', None)
            log_security_event(
                request=request,
                user=user,
                event_type='mfa_success',
                description='Успешная проверка демонстрационного MFA',
                risk_level='low',
            )
            _finish_login(request, user)
            return redirect('dashboard')
        log_security_event(
            request=request,
            user=user,
            event_type='mfa_failed',
            description='Неверный демонстрационный MFA-код',
            risk_level='high',
        )
        messages.error(request, 'Неверный код. Для демо используйте 123456.')
    return render(request, 'accounts/mfa.html', {'demo_code': '123456'})


def _finish_login(request, user):
    login(request, user)
    profile = user.profile
    profile.last_login_at = timezone.now()
    profile.save(update_fields=['last_login_at'])
    remember_trusted_device(request, user)
    log_security_event(
        request=request,
        user=user,
        event_type='login_success',
        description='Успешный вход в систему',
        risk_level='low',
    )


@login_required
def logout_view(request):
    log_security_event(
        request=request,
        event_type='logout',
        description='Выход из системы',
        risk_level='low',
    )
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_security_event(
            request=request,
            event_type='profile_update',
            description='Обновление профиля пользователя',
            risk_level='low',
        )
        messages.success(request, 'Профиль обновлен.')
        return redirect('accounts:profile')
    devices = TrustedDevice.objects.filter(user=request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'devices': devices})


@require_roles(ADMIN)
def users_list(request):
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'accounts/users_list.html', {'users': users})


@require_roles(ADMIN)
def user_role_update(request, pk):
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    old_role = user.profile.role
    form = UserRoleForm(request.POST or None, instance=user.profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if old_role != user.profile.role:
            log_security_event(
                request=request,
                event_type='role_changed',
                description=f'Роль пользователя {user.username} изменена: {old_role} -> {user.profile.role}',
                risk_level='medium',
            )
        messages.success(request, 'Права пользователя обновлены.')
        return redirect('accounts:users')
    return render(request, 'accounts/user_form.html', {'form': form, 'edited_user': user})


def permission_denied_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def not_found_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)
