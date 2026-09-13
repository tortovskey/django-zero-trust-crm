from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('mfa/', views.mfa_view, name='mfa'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.users_list, name='users'),
    path('users/<int:pk>/role/', views.user_role_update, name='user_role_update'),
]
