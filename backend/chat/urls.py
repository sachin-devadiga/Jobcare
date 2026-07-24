from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<uuid:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/mark-read/', views.MarkAsReadView.as_view(), name='message-mark-read'),
    path('messages/unread-count/', views.UnreadCountView.as_view(), name='message-unread-count'),
]
