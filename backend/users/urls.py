from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.EmployeeProfileView.as_view(), name='user-profile'),
    path('profile/avatar/', views.ProfileAvatarUploadView.as_view(), name='user-profile-avatar'),
    path('profile/voice-resume/', views.ProfileVoiceResumeUploadView.as_view(), name='user-profile-voice-resume'),
    path('profile/<uuid:pk>/', views.EmployeeProfileDetailView.as_view(), name='user-profile-detail'),
    path('profile/completion-score/', views.ProfileCompletionView.as_view(), name='user-profile-completion'),
]
