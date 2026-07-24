from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.ApplyForJobView.as_view(), name='application-apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='application-my'),
    path('<uuid:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('<uuid:pk>/status/', views.ApplicationStatusUpdateView.as_view(), name='application-status'),
    path('<uuid:pk>/interview/', views.ApplicationInterviewView.as_view(), name='application-interview'),
    path('<uuid:pk>/withdraw/', views.WithdrawApplicationView.as_view(), name='application-withdraw'),
    path('job/<uuid:job_id>/', views.JobApplicationsView.as_view(), name='application-job-list'),
]
