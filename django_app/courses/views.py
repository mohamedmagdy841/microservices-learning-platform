from .pagination import CustomPagination
from rest_framework import generics, permissions
from .permissions import HasActiveSubscription

from .serializers import (
    CategorySerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer
)
from .models import (
    Category,
    Course,
    Enrollment,
    LessonProgress
)

# ------------------------
# Category Views
# ------------------------
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

# ------------------------
# Course Views
# ------------------------
class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    pagination_class = CustomPagination
    queryset = (
        Course.objects
        .filter(is_published=True)
        .select_related("category")
        .prefetch_related("modules", "enrollments")
        .order_by("-created_at")
    )

class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    queryset = (
        Course.objects
        .filter(is_published=True)
        .select_related("category")
        .prefetch_related("modules", "modules__lessons")
    )
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    

# ------------------------
# Enrollment Views
# ------------------------
class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    pagination_class = CustomPagination
    permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        return (
            Enrollment.objects.filter(user=self.request.user)
            .select_related("course__category")
            .prefetch_related("course__modules", "course__enrollments")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EnrollmentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        return (
            Enrollment.objects.filter(user=self.request.user)
            .select_related("course__category")
            .prefetch_related("course__modules", "course__enrollments")
        )


# ------------------------
# Lesson Progress Views
# ------------------------
class LessonProgressListView(generics.ListAPIView):
    serializer_class = LessonProgressSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        return (
            LessonProgress.objects.filter(enrollment__user=self.request.user)
            .select_related("lesson", "enrollment__course")
        )
