from django.conf import settings
from django.db import models
from django.utils import timezone

from clients.models import Client


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В работе'
        WAITING_CLIENT = 'waiting_client', 'Ожидает клиента'
        CLOSED = 'closed', 'Закрыта'
        REJECTED = 'rejected', 'Отклонена'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        CRITICAL = 'critical', 'Критический'

    number = models.CharField('Номер заявки', max_length=30, unique=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    subject = models.CharField('Тема', max_length=180)
    description = models.TextField('Описание')
    status = models.CharField('Статус', max_length=30, choices=Status.choices, default=Status.NEW)
    priority = models.CharField('Приоритет', max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    responsible_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_tickets',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    closed_at = models.DateTimeField('Дата закрытия', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.status in {self.Status.CLOSED, self.Status.REJECTED} and not self.closed_at:
            self.closed_at = timezone.now()
        if self.status not in {self.Status.CLOSED, self.Status.REJECTED}:
            self.closed_at = None
        super().save(*args, **kwargs)
        if not self.number:
            self.number = f'T-{timezone.now().year}-{self.pk:04d}'
            super().save(update_fields=['number'])

    def __str__(self):
        return f'{self.number or "T-new"}: {self.subject}'
