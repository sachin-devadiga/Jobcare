from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='auth-verify-otp'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='auth-reset-password'),
    path('refresh/', views.RefreshView.as_view(), name='auth-refresh'),
    path('phone/send-otp/', views.SendPhoneOTPView.as_view(), name='auth-phone-send-otp'),
    path('otp/resend/', views.SendPhoneOTPView.as_view(), name='auth-otp-resend'),
    path('phone/verify/', views.VerifyPhoneOTPView.as_view(), name='auth-phone-verify'),
    path('phone/verify-firebase/', views.FirebasePhoneVerifyView.as_view(), name='auth-phone-verify-firebase'),
    path('otp/email/request/', views.EmailOTPRequestView.as_view(), name='auth-email-otp-request'),
    path('otp/email/verify/', views.EmailOTPVerifyView.as_view(), name='auth-email-otp-verify'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('profile/', views.ProfileView.as_view(), name='auth-profile'),
]
