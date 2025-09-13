from django.urls import path
from .views import (
    QuizAttemptListCreateView,
    QuizAttemptDetailView,
    QuizGradingCallbackView,
)

urlpatterns = [
    path("attempts/", QuizAttemptListCreateView.as_view()),
    path("attempts/<int:pk>/", QuizAttemptDetailView.as_view()),
    
    path("grading-callback/", QuizGradingCallbackView.as_view()),
]
