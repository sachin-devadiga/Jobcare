from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListCreateView.as_view(), name='job-list-create'),
    path('nearby/', views.NearbyJobsView.as_view(), name='job-nearby'),
    path('my-listings/', views.EmployerJobListView.as_view(), name='job-my-listings'),
    path('categories/', views.CategoryListView.as_view(), name='job-categories'),
    path('skills/', views.SkillListView.as_view(), name='job-skills'),
    path('cities/', views.CityListView.as_view(), name='job-cities'),
    path('<uuid:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    path('<uuid:pk>/status/', views.JobStatusView.as_view(), name='job-status'),
]
