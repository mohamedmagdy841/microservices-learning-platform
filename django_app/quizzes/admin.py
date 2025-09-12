from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Quiz, Question, QuizAttempt, QuizAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = ("id", "title", "module", "created_at")
    list_filter = ("created_at", "module")
    search_fields = ("title", "module__title")
    inlines = [QuestionInline]


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    readonly_fields = ("question", "chosen_answer", "is_correct")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(ModelAdmin):
    list_display = ("id", "user", "quiz", "score", "passed", "attempt_date")
    list_filter = ("passed", "attempt_date", "quiz")
    search_fields = ("user__email", "quiz__title")
    readonly_fields = ("score", "passed", "attempt_date")
    inlines = [QuizAnswerInline]


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ("id", "quiz", "text", "correct_answer")
    search_fields = ("text", "quiz__title")


@admin.register(QuizAnswer)
class QuizAnswerAdmin(ModelAdmin):
    list_display = ("id", "attempt", "question", "chosen_answer", "is_correct")
    list_filter = ("is_correct", "question__quiz")
    search_fields = ("chosen_answer", "question__text")

