from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from courses.models import Course

class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["course"],
                name="unique_quiz_per_course"
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.course})"


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.TextField()
    correct_answer = models.CharField(max_length=255, blank=True, null=True)
    options = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Q{self.id} - {self.text[:50]}"
    
    def clean(self):
        if self.quiz.questions.count() >= 5 and not self.pk:
            raise ValidationError("A quiz cannot have more than 5 questions.")


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts"
    )
    score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    attempt_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempt_date"]

    def __str__(self):
        return f"{self.user} - {self.quiz} ({'Passed' if self.passed else 'Failed'})"


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    chosen_answer = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer {self.id} - Attempt {self.attempt_id} - {self.chosen_answer}"
