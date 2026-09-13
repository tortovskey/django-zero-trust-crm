from django.urls import path

from . import views

app_name = 'gdpr'

urlpatterns = [
    path('', views.gdpr_home, name='home'),
    path('export/', views.export_my_data, name='export_my_data'),
    path('deletion-requests/', views.deletion_request_list, name='deletion_requests'),
    path('deletion-requests/new/', views.deletion_request_create, name='deletion_request_create'),
    path('deletion-requests/<int:pk>/review/', views.deletion_request_update, name='deletion_request_update'),
    path('policy/', views.data_policy, name='policy'),
]
