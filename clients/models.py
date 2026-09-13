from django.conf import settings
from django.db import models


class Client(models.Model):
    class ClientType(models.TextChoices):
        INDIVIDUAL = 'individual', 'Физическое лицо'
        COMPANY = 'company', 'Компания'
        PARTNER = 'partner', 'Партнер'

    class ConsentStatus(models.TextChoices):
        GIVEN = 'given', 'Согласие получено'
        WITHDRAWN = 'withdrawn', 'Согласие отозвано'
        EXPIRED = 'expired', 'Истекло'
        UNKNOWN = 'unknown', 'Не указано'

    full_name = models.CharField('ФИО / название', max_length=180)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=40, blank=True)
    address = models.TextField('Адрес', blank=True)
    client_type = models.CharField('Тип клиента', max_length=20, choices=ClientType.choices)
    registration_date = models.DateField('Дата регистрации', auto_now_add=True)
    personal_data_consent = models.BooleanField('Согласие на обработку данных', default=False)
    consent_date = models.DateField('Дата согласия', null=True, blank=True)
    consent_status = models.CharField(
        'Статус согласия',
        max_length=20,
        choices=ConsentStatus.choices,
        default=ConsentStatus.UNKNOWN,
    )
    processing_purpose = models.CharField(
        'Цель обработки',
        max_length=240,
        default='Обработка клиентских заявок и сопровождение сервиса',
    )
    comment = models.TextField('Комментарий', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_clients',
    )

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name
