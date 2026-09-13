from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from clients.models import Client
from gdpr.models import ConsentRecord, DataDeletionRequest
from security.models import SecurityEvent, TrustedDevice
from tickets.models import Ticket


class Command(BaseCommand):
    help = 'Creates demo users, clients, tickets and audit data for KOSTY.'

    def handle(self, *args, **options):
        users = {
            'admin': ('admin12345', Profile.Role.ADMIN, True, True),
            'manager': ('manager12345', Profile.Role.MANAGER, False, True),
            'security': ('security12345', Profile.Role.SECURITY, False, True),
            'auditor': ('auditor12345', Profile.Role.AUDITOR, False, False),
            'user': ('user12345', Profile.Role.USER, False, False),
        }

        created_users = {}
        for username, (password, role, is_superuser, mfa_enabled) in users.items():
            user, _ = User.objects.get_or_create(username=username, defaults={'email': f'{username}@kosty.local'})
            user.set_password(password)
            user.is_staff = role == Profile.Role.ADMIN
            user.is_superuser = is_superuser
            user.first_name = username.capitalize()
            user.email = f'{username}@kosty.local'
            user.save()
            profile = user.profile
            profile.role = role
            profile.department = self._department_for(role)
            profile.phone = '+7 900 000-00-00'
            profile.is_active_profile = True
            profile.mfa_enabled = mfa_enabled
            profile.save()
            created_users[username] = user

        clients_data = [
            {
                'full_name': 'Иван Петров',
                'email': 'ivan.petrov@example.com',
                'phone': '+7 900 111-22-33',
                'address': 'Москва, ул. Учебная, 10',
                'client_type': Client.ClientType.INDIVIDUAL,
                'personal_data_consent': True,
                'consent_date': timezone.localdate(),
                'consent_status': Client.ConsentStatus.GIVEN,
                'comment': 'Клиент интересуется сопровождением договора.',
            },
            {
                'full_name': 'ООО "Север"',
                'email': 'office@sever.example.com',
                'phone': '+7 900 222-33-44',
                'address': 'Санкт-Петербург, Невский пр., 15',
                'client_type': Client.ClientType.COMPANY,
                'personal_data_consent': True,
                'consent_date': timezone.localdate(),
                'consent_status': Client.ConsentStatus.GIVEN,
                'comment': 'Корпоративный клиент.',
            },
            {
                'full_name': 'Анна Смирнова',
                'email': 'anna.smirnova@example.com',
                'phone': '+7 900 333-44-55',
                'address': 'Казань, ул. Демонстрационная, 7',
                'client_type': Client.ClientType.INDIVIDUAL,
                'personal_data_consent': False,
                'consent_status': Client.ConsentStatus.UNKNOWN,
                'comment': 'Нужно запросить согласие перед обработкой.',
            },
        ]

        clients = []
        for data in clients_data:
            client, _ = Client.objects.update_or_create(
                email=data['email'],
                defaults={**data, 'created_by': created_users['manager']},
            )
            clients.append(client)
            ConsentRecord.objects.get_or_create(
                client=client,
                purpose=client.processing_purpose,
                defaults={
                    'is_given': client.personal_data_consent,
                    'comment': 'Seed-запись согласия для демонстрации GDPR.',
                },
            )

        ticket_data = [
            (clients[0], 'Проверить статус договора', Ticket.Priority.MEDIUM, Ticket.Status.IN_PROGRESS),
            (clients[1], 'Настроить доступ для сотрудников', Ticket.Priority.HIGH, Ticket.Status.NEW),
            (clients[2], 'Запросить согласие GDPR', Ticket.Priority.CRITICAL, Ticket.Status.WAITING_CLIENT),
        ]
        for client, subject, priority, status in ticket_data:
            ticket, _ = Ticket.objects.get_or_create(
                client=client,
                subject=subject,
                defaults={
                    'description': f'Учебная заявка: {subject}.',
                    'priority': priority,
                    'status': status,
                    'responsible_manager': created_users['manager'],
                    'requester': created_users['manager'],
                },
            )
            if not ticket.number:
                ticket.save()

        Ticket.objects.get_or_create(
            subject='Личная заявка пользователя',
            requester=created_users['user'],
            defaults={
                'description': 'Обычный пользователь видит только эту заявку.',
                'priority': Ticket.Priority.LOW,
                'status': Ticket.Status.NEW,
            },
        )

        DataDeletionRequest.objects.get_or_create(
            user=created_users['user'],
            reason='Демонстрационный запрос на удаление персональных данных после окончания обработки.',
            defaults={'status': DataDeletionRequest.Status.NEW},
        )

        SecurityEvent.objects.get_or_create(
            user=created_users['admin'],
            event_type=SecurityEvent.EventType.LOGIN_SUCCESS,
            description='Seed-событие успешного входа администратора.',
            defaults={'risk_level': SecurityEvent.RiskLevel.LOW, 'ip_address': '127.0.0.1'},
        )
        SecurityEvent.objects.get_or_create(
            user=created_users['user'],
            event_type=SecurityEvent.EventType.ACCESS_DENIED,
            description='Seed-событие отказа в доступе к административной странице.',
            defaults={'risk_level': SecurityEvent.RiskLevel.MEDIUM, 'ip_address': '127.0.0.1'},
        )
        TrustedDevice.objects.get_or_create(
            user=created_users['admin'],
            user_agent='Seed Browser',
            ip_address='127.0.0.1',
            defaults={'name': 'Demo workstation', 'is_trusted': True},
        )

        self.stdout.write(self.style.SUCCESS('KOSTY seed data created.'))

    def _department_for(self, role):
        return {
            Profile.Role.ADMIN: 'Администрирование',
            Profile.Role.MANAGER: 'Клиентский сервис',
            Profile.Role.SECURITY: 'Информационная безопасность',
            Profile.Role.AUDITOR: 'Аудит',
            Profile.Role.USER: 'Пользователи',
        }[role]
