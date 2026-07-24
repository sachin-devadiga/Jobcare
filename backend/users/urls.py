from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.EmployeeProfileView.as_view(), name='user-profile'),
    path('profile/<uuid:pk>/', views.EmployeeProfileDetailView.as_view(), name='user-profile-detail'),
    path('profile/completion-score/', views.ProfileCompletionView.as_view(), name='user-profile-completion'),
]
