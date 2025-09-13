from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import QuizAttempt, QuizAnswer
from .serializers import (
    QuizAttemptSerializer,
    QuizAttemptCreateSerializer,
)
from . import producers
from subscriptions.permissions import IsServiceToken

# ------------------------
# Student Quiz Attempts
# ------------------------
class QuizAttemptListCreateView(generics.ListCreateAPIView):
    """
    GET: List student's attempts
    POST: Create a new attempt and publish event to RabbitMQ
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user).prefetch_related("answers")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return QuizAttemptCreateSerializer
        return QuizAttemptSerializer

    def perform_create(self, serializer):
        attempt = serializer.save(user=self.request.user)

        # prepare answers for RabbitMQ
        answers = [
            {"question_id": ans.question.id, "chosen_answer": ans.chosen_answer}
            for ans in attempt.answers.all()
        ]

        # publish quiz_submitted event
        producers.publish_quiz_submitted_event(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz.id,
            user_id=attempt.user.id,
            answers=answers,
        )


class QuizAttemptDetailView(generics.RetrieveAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user).prefetch_related("answers")


# ------------------------
# Callback from FastAPI AI Grader
# ------------------------
class QuizGradingCallbackView(APIView):
    """
    Consumed only by FastAPI AI grader via service token.
    Updates score, passed status, and marks answers correct/incorrect.
    """
    permission_classes = [IsServiceToken]

    def post(self, request, *args, **kwargs):
        data = request.data
        attempt = get_object_or_404(QuizAttempt, id=data["attempt_id"])

        # update attempt
        attempt.score = data["score"]
        attempt.passed = data["passed"]
        attempt.save(update_fields=["score", "passed"])

        # update answers correctness
        for ans in data["answers"]:
            QuizAnswer.objects.filter(
                attempt=attempt, question_id=ans["question_id"]
            ).update(is_correct=ans["is_correct"])

        return Response({"message": "Quiz graded successfully"}, status=status.HTTP_200_OK)
