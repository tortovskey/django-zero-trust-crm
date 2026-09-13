from django.conf import settings
from django.db import models

from clients.models import Client


class DataDeletionRequestQuerySet(models.QuerySet):
    def visible_for(self, user):
        from accounts.rbac import ADMIN, AUDITOR, get_role

        if user.is_authenticated and get_role(user) in {ADMIN, AUDITOR}:
            return self
        if user.is_authenticated:
            return self.filter(user=user)
        return self.none()


class DataDeletionRequest(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        REVIEWING = 'reviewing', 'Рассматривается'
        COMPLETED = 'completed', 'Выполнен'
        REJECTED = 'rejected', 'Отклонен'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='data_deletion_requests',
    )
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='deletion_requests')
    reason = models.TextField('Причина')
    requested_at = models.DateTimeField('Дата запроса', auto_now_add=True)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.NEW)
    admin_comment = models.TextField('Комментарий администратора', blank=True)

    objects = DataDeletionRequestQuerySet.as_manager()

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        owner = self.user.username if self.user else self.client or 'unknown'
        return f'Запрос на удаление данных: {owner}'


class ConsentRecord(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='consent_records')
    purpose = models.CharField('Цель обработки', max_length=240)
    is_given = models.BooleanField('Согласие дано', default=True)
    recorded_at = models.DateTimeField('Дата фиксации', auto_now_add=True)
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.client} - {self.purpose}'
