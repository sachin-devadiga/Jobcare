from django.urls import path
from . import views

urlpatterns = [
    path('webhook/exotel/', views.ExotelIVRWebhookView.as_view(), name='exotel-ivr-webhook'),
    path('audio/question/<uuid:session_id>/', views.ServeQuestionAudioView.as_view(), name='serve-question-audio'),
]
