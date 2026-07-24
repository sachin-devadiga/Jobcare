from django.urls import path
from . import views

urlpatterns = [
    path('', views.CompanyListCreateView.as_view(), name='company-list-create'),
    path('<uuid:pk>/', views.CompanyDetailView.as_view(), name='company-detail'),
    path('<uuid:pk>/verify/', views.CompanyVerifyView.as_view(), name='company-verify'),
]
