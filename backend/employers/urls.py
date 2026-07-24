from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.EmployerProfileView.as_view(), name='employer-profile'),
    path('profile/<uuid:pk>/', views.EmployerProfileDetailView.as_view(), name='employer-profile-detail'),
    path('', views.EmployerProfileListView.as_view(), name='employer-list'),
]
