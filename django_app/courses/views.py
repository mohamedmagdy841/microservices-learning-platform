from .pagination import CustomPagination
from rest_framework import generics, permissions
from .permissions import HasActiveSubscription
from django.shortcuts import get_object_or_404
from .serializers import (
    CategorySerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer
)
from quizzes.serializers import QuizSerializer
from .models import (
    Category,
    Course,
    Enrollment,
    LessonProgress
)
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
)
from quizzes.models import Quiz

# ------------------------
# Category Views
# ------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Categories"],
        summary="List categories",
        description="Retrieve a paginated list of all categories.",
        responses={200: CategorySerializer},
    )
)
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

@extend_schema_view(
    get=extend_schema(
        tags=["Categories"],
        summary="Retrieve category details",
        description="Retrieve details of a single category by slug.",
        responses={200: CategorySerializer},
    )
)
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

# ------------------------
# Course Views
# ------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Courses"],
        summary="List published courses",
        description="Retrieve a paginated list of all published courses with categories and enrollments.",
        responses={200: CourseListSerializer},
    )
)
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

@extend_schema_view(
    get=extend_schema(
        tags=["Courses"],
        summary="Retrieve course details",
        description="Retrieve details of a single published course by slug, including modules and lessons.",
        responses={200: CourseDetailSerializer},
    )
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
@extend_schema_view(
    get=extend_schema(
        tags=["Enrollments"],
        summary="List user enrollments",
        description="Retrieve a paginated list of the authenticated user's course enrollments.",
        responses={200: EnrollmentSerializer},
    ),
    post=extend_schema(
        tags=["Enrollments"],
        summary="Create enrollment",
        description="Enroll the authenticated user into a course.",
        responses={201: EnrollmentSerializer},
    )
)
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


@extend_schema_view(
    get=extend_schema(
        tags=["Enrollments"],
        summary="Retrieve enrollment details",
        description="Retrieve details of a specific enrollment for the authenticated user.",
        responses={200: EnrollmentSerializer},
    ),
    delete=extend_schema(
        tags=["Enrollments"],
        summary="Unenroll from a course",
        description="Delete the specified enrollment (unenroll the user from the course).",
        responses={204: None},
    )
)
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
@extend_schema_view(
    get=extend_schema(
        tags=["Lesson Progress"],
        summary="List lesson progress",
        description="Retrieve a paginated list of lesson progress for the authenticated user.",
        responses={200: LessonProgressSerializer},
    )
)
class LessonProgressListView(generics.ListAPIView):
    serializer_class = LessonProgressSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        return (
            LessonProgress.objects.filter(enrollment__user=self.request.user)
            .select_related("lesson", "enrollment__course")
        )

# ------------------------
# Course Quiz View
# ------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Quizzes"],
        summary="Retrieve course quiz",
        description="Retrieve the quiz associated with a course by course ID, including questions.",
        responses={200: QuizSerializer},
    )
)
class CourseQuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        course_id = self.kwargs["course_id"]
        course = get_object_or_404(Course, id=course_id)
        return get_object_or_404(
            Quiz.objects.prefetch_related("questions"),
            course=course
        )
