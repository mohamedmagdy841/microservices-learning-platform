from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Category, Course, Enrollment, Module, Lesson, LessonProgress
)


# ---------- Inlines ----------
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ("title", "order_index")
    ordering = ("order_index",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "video_url", "order_index")
    ordering = ("order_index",)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fields = ("user", "progress", "enrolled_at")
    readonly_fields = ("enrolled_at",)


class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 1
    fields = ("lesson", "progress")
    ordering = ("lesson__order_index",)


# ---------- Admin Models ----------
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "description")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at")
    list_filter = ("is_published", "category")
    search_fields = ("title", "slug", "description", "category__name")
    ordering = ("-created_at",)
    inlines = [ModuleInline, EnrollmentInline]


@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ("title", "course", "order_index")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "order_index")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ("title", "module", "order_index", "video_url")
    list_filter = ("module__course",)
    search_fields = ("title", "module__title", "module__course__title")
    ordering = ("module", "order_index")


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ("user", "course", "progress", "enrolled_at")
    list_filter = ("course", "user")
    search_fields = ("user__username", "course__title")
    ordering = ("-enrolled_at",)
    inlines = [LessonProgressInline]


@admin.register(LessonProgress)
class LessonProgressAdmin(ModelAdmin):
    list_display = ("enrollment", "lesson", "progress", "is_completed")
    list_filter = ("lesson__module__course", "lesson__module")
    search_fields = (
        "enrollment__user__username",
        "lesson__title",
        "lesson__module__title",
        "lesson__module__course__title",
    )
    ordering = ("lesson__module__course", "lesson__order_index")
