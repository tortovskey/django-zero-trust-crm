from django.conf import settings
from django.db import models


class SecurityEvent(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = 'login_success', 'Успешный вход'
        LOGIN_FAILED = 'login_failed', 'Неуспешный вход'
        LOGOUT = 'logout', 'Выход'
        ACCESS_DENIED = 'access_denied', 'Отказ в доступе'
        ROLE_CHANGED = 'role_changed', 'Изменение роли'
        MFA_SUCCESS = 'mfa_success', 'Успешный MFA'
        MFA_FAILED = 'mfa_failed', 'Ошибка MFA'
        REGISTRATION = 'registration', 'Регистрация'
        PROFILE_UPDATE = 'profile_update', 'Обновление профиля'
        CLIENT_CREATED = 'client_created', 'Создание клиента'
        CLIENT_UPDATED = 'client_updated', 'Обновление клиента'
        CLIENT_DELETED = 'client_deleted', 'Удаление клиента'
        TICKET_CREATED = 'ticket_created', 'Создание заявки'
        TICKET_UPDATED = 'ticket_updated', 'Обновление заявки'
        DATA_EXPORT = 'data_export', 'Экспорт данных'
        DATA_DELETION_REQUEST = 'data_deletion_request', 'Запрос на удаление данных'

    class RiskLevel(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_events',
    )
    event_type = models.CharField('Тип события', max_length=40, choices=EventType.choices)
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True)
    created_at = models.DateTimeField('Дата и время', auto_now_add=True)
    description = models.TextField('Описание')
    risk_level = models.CharField('Уровень риска', max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else 'anonymous'
        return f'{self.get_event_type_display()} - {username}'


class TrustedDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trusted_devices')
    name = models.CharField('Название устройства', max_length=120)
    user_agent = models.TextField('User-Agent')
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    first_seen_at = models.DateTimeField('Первый вход', auto_now_add=True)
    last_seen_at = models.DateTimeField('Последний вход', auto_now=True)
    is_trusted = models.BooleanField('Доверенное', default=False)

    class Meta:
        ordering = ['-last_seen_at']
        unique_together = ('user', 'user_agent', 'ip_address')

    def __str__(self):
        return f'{self.name} - {self.user.username}'
