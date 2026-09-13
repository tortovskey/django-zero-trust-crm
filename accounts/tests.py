from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from clients.models import Client
from security.models import SecurityEvent
from tickets.models import Ticket


class AccessControlTests(TestCase):
    def setUp(self):
        self.admin = self._user('admin', Profile.Role.ADMIN)
        self.manager = self._user('manager', Profile.Role.MANAGER)
        self.auditor = self._user('auditor', Profile.Role.AUDITOR)
        self.user = self._user('user', Profile.Role.USER)
        self.client_record = Client.objects.create(
            full_name='Тестовый клиент',
            email='client@example.com',
            phone='+7 900 000-00-01',
            client_type=Client.ClientType.INDIVIDUAL,
            personal_data_consent=True,
            consent_status=Client.ConsentStatus.GIVEN,
            created_by=self.manager,
        )

    def _user(self, username, role):
        user = User.objects.create_user(username=username, password='password12345')
        user.profile.role = role
        user.profile.save()
        return user

    def test_regular_user_cannot_open_all_clients(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('clients:list'))
        self.assertEqual(response.status_code, 403)

    def test_manager_can_create_ticket(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse('tickets:create'),
            {
                'client': self.client_record.pk,
                'subject': 'Новая заявка',
                'description': 'Описание заявки',
                'status': Ticket.Status.NEW,
                'priority': Ticket.Priority.HIGH,
                'responsible_manager': self.manager.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ticket.objects.filter(subject='Новая заявка').exists())

    def test_auditor_cannot_edit_client(self):
        self.client.force_login(self.auditor)
        response = self.client.get(reverse('clients:update', args=[self.client_record.pk]))
        self.assertEqual(response.status_code, 403)

    def test_security_event_created_on_access_denied(self):
        self.client.force_login(self.user)
        before = SecurityEvent.objects.filter(event_type=SecurityEvent.EventType.ACCESS_DENIED).count()
        self.client.get(reverse('clients:list'))
        after = SecurityEvent.objects.filter(event_type=SecurityEvent.EventType.ACCESS_DENIED).count()
        self.assertEqual(after, before + 1)

    def test_data_export_returns_json(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('gdpr:export_my_data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('user', response.json())
