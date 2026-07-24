from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='payment-plans'),
    path('create-order/', views.CreatePaymentOrderView.as_view(), name='payment-create-order'),
    path('verify/', views.VerifyPaymentView.as_view(), name='payment-verify'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('subscriptions/', views.MySubscriptionsView.as_view(), name='payment-subscriptions'),
    path('subscriptions/create/', views.CreateSubscriptionView.as_view(), name='payment-subscription-create'),
    path('subscriptions/<uuid:pk>/cancel/', views.CancelSubscriptionView.as_view(), name='payment-subscription-cancel'),
]
