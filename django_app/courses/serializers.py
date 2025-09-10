from rest_framework import serializers
from .models import (
    Category,
    Course,
    Module,
    Lesson,
    Enrollment,
    LessonProgress
)

# ------------------------
# Category
# ------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


# ------------------------
# Lesson Progress
# ------------------------
class LessonProgressSerializer(serializers.ModelSerializer):
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = LessonProgress
        fields = ["id", "lesson", "progress", "is_completed"]


# ------------------------
# Lesson
# ------------------------
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "order_index"]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context["request"].user
        from subscriptions.utils import has_active_subscription
        
        if not (user.is_authenticated and has_active_subscription(user)):
            data.pop("video_url", None)
        return data


# ------------------------
# Module (with lessons)
# ------------------------
class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "order_index", "lessons"]


# ------------------------
# Course (list)
# ------------------------
class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    modules_count = serializers.IntegerField(source="modules.count", read_only=True)
    students_count = serializers.IntegerField(source="enrollments.count", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "is_published",
            "category",
            "modules_count",
            "students_count",
            "created_at",
        ]


# ------------------------
# Course (detail)
# ------------------------
class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "thumbnail",
            "is_published",
            "category",
            "modules",
            "created_at",
        ]


# ------------------------
# Enrollment
# ------------------------
class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_id", "progress", "enrolled_at"]

    def validate_course_id(self, value):
        user = self.context["request"].user
        if Enrollment.objects.filter(user=user, course=value).exists():
            raise serializers.ValidationError("Already enrolled in this course.")
        return value

