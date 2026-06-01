from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.MeView.as_view(), name='me'),
    path('me/avatar/', views.AvatarUploadView.as_view(), name='avatar-upload'),
    path('me/delete/', views.DeleteAccountView.as_view(), name='delete-account'),
    path('me/partner-role/', views.PartnerRoleToggleView.as_view(), name='partner-role-toggle'),
    path('google/', views.GoogleAuthView.as_view(), name='google-auth'),
    # Password reset
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
