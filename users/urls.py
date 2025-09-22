from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('auth/verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password/forgot/', views.ForgotPasswordView.as_view(), name='password-forgot'),
    path('password/reset/', views.ResetPasswordView.as_view(), name='password-reset'),
    path('password/change/', views.ChangePasswordView.as_view(), name='password-change'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('premium/status/', views.PremiumStatusView.as_view(), name='premium-status'),
    path('premium/upgrade/', views.PremiumUpgradeView.as_view(), name='premium-upgrade'),
    path('premium/grant/', views.PremiumGrantView.as_view(), name='premium-grant'),
    path('test-email/', views.TestEmailView.as_view(), name='test-email'),
] 