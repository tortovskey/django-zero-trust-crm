from django.urls import path

from . import views

app_name = 'security'

urlpatterns = [
    path('events/', views.event_list, name='events'),
    path('devices/', views.device_list, name='devices'),
]
