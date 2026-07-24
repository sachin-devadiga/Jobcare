from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', views.UnreadNotificationCountView.as_view(), name='notification-unread-count'),
    path('<uuid:pk>/read/', views.MarkNotificationReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='notification-mark-all-read'),
    path('devices/', views.DeviceRegistrationView.as_view(), name='notification-devices'),
    path('send/', views.SendNotificationAdminView.as_view(), name='notification-send'),
]
