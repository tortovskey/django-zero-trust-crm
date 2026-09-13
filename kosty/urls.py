from django.contrib import admin
from django.urls import include, path

from accounts import views as account_views

urlpatterns = [
    path('', account_views.dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('clients/', include('clients.urls')),
    path('tickets/', include('tickets.urls')),
    path('security/', include('security.urls')),
    path('gdpr/', include('gdpr.urls')),
]

handler403 = 'accounts.views.permission_denied_view'
handler404 = 'accounts.views.not_found_view'
