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
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)

# ------------------------
# Student Quiz Attempts
# ------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Quiz Attempts"],
        summary="List quiz attempts",
        description="Retrieve a paginated list of the authenticated student's quiz attempts.",
        responses={200: QuizAttemptSerializer},
    ),
    post=extend_schema(
        tags=["Quiz Attempts"],
        summary="Create a new quiz attempt",
        description="Create a quiz attempt for the authenticated student and publish an event to RabbitMQ.",
        request=QuizAttemptCreateSerializer,
        responses={201: QuizAttemptSerializer},
    )
)
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
            {
                "question_id": ans.question.id,
                "question_text": ans.question.text,
                "correct_answer": ans.question.correct_answer,
                "chosen_answer": ans.chosen_answer,
            }
            for ans in attempt.answers.select_related("question").all()
        ]

        # publish quiz_submitted event
        producers.publish_quiz_submitted_event(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz.id,
            user_id=attempt.user.id,
            answers=answers,
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Quiz Attempts"],
        summary="Retrieve quiz attempt details",
        description="Retrieve details of a specific quiz attempt belonging to the authenticated student.",
        responses={200: QuizAttemptSerializer},
    )
)
class QuizAttemptDetailView(generics.RetrieveAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user).prefetch_related("answers")


# ------------------------
# Callback from FastAPI AI Grader
# ------------------------
@extend_schema_view(
    post=extend_schema(
        tags=["Quiz Grading"],
        summary="Quiz grading callback",
        description=(
            "Endpoint consumed only by the FastAPI AI Grader service. "
            "Updates the quiz attempt's score, passed status, and marks answers correct/incorrect."
        ),
        auth=[],  # secured via service token, not standard user auth
        request={
            "application/json": OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                "Quiz grading example",
                value={
                    "attempt_id": 12,
                    "score": 85,
                    "passed": True,
                    "answers": [
                        {
                            "question_id": 5,
                            "is_correct": True
                        },
                        {
                            "question_id": 6,
                            "is_correct": False
                        }
                    ]
                },
            )
        ],
        responses={200: OpenApiResponse(description="Quiz graded successfully")},
    )
)
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
