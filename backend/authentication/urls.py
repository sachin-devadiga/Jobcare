from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='auth-verify-otp'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='auth-reset-password'),
    path('refresh/', views.RefreshView.as_view(), name='auth-refresh'),
    path('phone/request-otp/', views.PhoneRequestOTPView.as_view(), name='auth-phone-request-otp'),
    path('phone/verify-otp/', views.PhoneVerifyOTPView.as_view(), name='auth-phone-verify-otp'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('profile/', views.ProfileView.as_view(), name='auth-profile'),
]
