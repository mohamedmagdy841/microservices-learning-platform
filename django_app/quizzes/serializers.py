from rest_framework import serializers
from .models import Quiz, Question, QuizAttempt, QuizAnswer


# ------------------------
# Question
# ------------------------
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "options", "correct_answer"]
        extra_kwargs = {
            "correct_answer": {"write_only": True},
        }


# ------------------------
# Quiz (with questions)
# ------------------------
class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "course", "created_at", "questions"]


# ------------------------
# QuizAnswer
# ------------------------
class QuizAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(
        source="question.text", read_only=True
    )

    class Meta:
        model = QuizAnswer
        fields = ["id", "question", "question_text", "chosen_answer", "is_correct"]
        read_only_fields = ["is_correct"]


# ------------------------
# QuizAttempt
# ------------------------
class QuizAttemptSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ["id", "user", "quiz", "score", "passed", "attempt_date", "answers"]
        read_only_fields = ["score", "passed", "attempt_date", "user"]


# ------------------------
# Student attempt creation
# ------------------------
class QuizAnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ["question", "chosen_answer"]


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    answers = QuizAnswerCreateSerializer(many=True)

    class Meta:
        model = QuizAttempt
        fields = ["quiz", "answers"]

    def create(self, validated_data):
        user = self.context["request"].user
        quiz = validated_data["quiz"]
        answers_data = validated_data.pop("answers")

        attempt = QuizAttempt.objects.create(user=user, quiz=quiz)

        # save answers
        for ans in answers_data:
            QuizAnswer.objects.create(
                attempt=attempt,
                question=ans["question"],
                chosen_answer=ans["chosen_answer"],
                is_correct=False  # AI will evaluate later
            )

        return attempt
