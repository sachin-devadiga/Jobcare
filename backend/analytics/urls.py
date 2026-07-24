from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardStatsView.as_view(), name='analytics-dashboard'),
    path('jobs/<uuid:pk>/', views.JobAnalyticsView.as_view(), name='analytics-job'),
    path('applications/', views.ApplicationAnalyticsView.as_view(), name='analytics-applications'),
]

urlpatterns += [
    path('ai/', include('analytics.ai_urls')),
]
