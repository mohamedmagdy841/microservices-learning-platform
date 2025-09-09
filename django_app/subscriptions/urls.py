from django.urls import path
from .views import (
    SubscriptionPlanListView,
    SubscriptionPlanDetailView,
    SubscriptionListView,
    SubscriptionDetailView,
    PaymentListView,
    PaymentDetailView,
)

urlpatterns = [
    # Subscription Plans
    path("plans/", SubscriptionPlanListView.as_view()),
    path("plans/<int:pk>/", SubscriptionPlanDetailView.as_view()),

    # Payments
    path("payments/", PaymentListView.as_view()),
    path("payments/<int:pk>/", PaymentDetailView.as_view()),
    
    # Subscriptions
    path("", SubscriptionListView.as_view()),
    path("<int:pk>/", SubscriptionDetailView.as_view()),
]
