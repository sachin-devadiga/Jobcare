from django.urls import path
from . import views

urlpatterns = [
    path('webhook/exotel/', views.ExotelIVRWebhookView.as_view(), name='exotel-ivr-webhook'),
    path('webhook/plivo/', views.PlivoIVRWebhookView.as_view(), name='plivo-ivr-webhook'),
    path('webhook/plivo/hangup/', views.PlivoHangupView.as_view(), name='plivo-ivr-hangup'),
    path('audio/question/<uuid:session_id>/', views.ServeQuestionAudioView.as_view(), name='serve-question-audio'),
]
