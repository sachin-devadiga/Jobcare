from django.urls import path
from . import ai_views

urlpatterns = [
    path('resume-score/', ai_views.ResumeScoreView.as_view(), name='ai-resume-score'),
    path('skill-gap/', ai_views.SkillGapView.as_view(), name='ai-skill-gap'),
    path('upskilling/', ai_views.UpskillingView.as_view(), name='ai-upskilling'),
    path('salary-prediction/', ai_views.SalaryPredictionView.as_view(), name='ai-salary-prediction'),
    path('career-recommendations/', ai_views.CareerRecommendationView.as_view(), name='ai-career-recommendations'),
    path('job-recommendations/', ai_views.JobRecommendationView.as_view(), name='ai-job-recommendations'),
    path('fraud-check/', ai_views.FraudCheckView.as_view(), name='ai-fraud-check'),
]
