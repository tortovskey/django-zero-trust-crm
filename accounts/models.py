from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        SECURITY = 'security', 'Специалист по безопасности'
        AUDITOR = 'auditor', 'Аудитор'
        USER = 'user', 'Обычный пользователь'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    department = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    is_active_profile = models.BooleanField(default=True)
    mfa_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
