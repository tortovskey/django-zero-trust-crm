from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Profile


ADMIN = Profile.Role.ADMIN
MANAGER = Profile.Role.MANAGER
SECURITY = Profile.Role.SECURITY
AUDITOR = Profile.Role.AUDITOR
USER = Profile.Role.USER


def get_role(user):
    if not user.is_authenticated:
        return None
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.role


def is_active_kosty_user(user):
    if not user.is_authenticated or not user.is_active:
        return False
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.is_active_profile


def log_denied(request, description):
    from security.services import log_security_event

    log_security_event(
        request=request,
        event_type='access_denied',
        description=description,
        risk_level='medium',
    )


def require_roles(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not is_active_kosty_user(request.user):
                log_denied(request, 'Попытка доступа неактивного пользователя')
                raise PermissionDenied
            if request.session.get('suspicious'):
                log_denied(request, 'Сессия помечена как подозрительная')
                raise PermissionDenied
            if roles and get_role(request.user) not in roles:
                log_denied(request, f'Недостаточно прав для страницы {request.path}')
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def redirect_by_role(user):
    role = get_role(user)
    if role == ADMIN:
        return redirect('accounts:users')
    if role == SECURITY:
        return redirect('security:events')
    if role == USER:
        return redirect('tickets:list')
    return redirect('dashboard')


def can_edit_business_data(user):
    return get_role(user) in {ADMIN, MANAGER}


def can_read_business_data(user):
    return get_role(user) in {ADMIN, MANAGER, AUDITOR}


def can_view_security(user):
    return get_role(user) in {ADMIN, SECURITY, AUDITOR}
