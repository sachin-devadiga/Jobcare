from django.urls import path
from . import views

urlpatterns = [
    path('speech-to-text/', views.SpeechToTextView.as_view(), name='voice-speech-to-text'),
    path('text-to-speech/', views.TextToSpeechView.as_view(), name='voice-text-to-speech'),
    path('search/', views.VoiceSearchView.as_view(), name='voice-search'),
    path('navigate/', views.VoiceNavigationView.as_view(), name='voice-navigate'),
    path('history/', views.VoiceSessionHistoryView.as_view(), name='voice-history'),
    path('extract-profile/', views.ExtractProfileView.as_view(), name='voice-extract-profile'),
    path('build-resume/', views.BuildResumeView.as_view(), name='voice-build-resume'),
]
