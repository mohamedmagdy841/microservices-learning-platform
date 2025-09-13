from django.urls import path
from .views import (
    CourseListView,
    CourseDetailView,
    CategoryListView,
    CategoryDetailView,
    EnrollmentListCreateView,
    LessonProgressListView,
    EnrollmentDetailView,
    CourseQuizDetailView
)
urlpatterns = [    
    # ------------------------
    # Category Endpoints
    # ------------------------
    path("categories/", CategoryListView.as_view()),
    path("categories/<slug:slug>/", CategoryDetailView.as_view()),
    
    # ------------------------
    # Enrollment Endpoints
    # ------------------------
    path("enrollments/", EnrollmentListCreateView.as_view()),
    path("enrollments/<int:pk>/", EnrollmentDetailView.as_view()),

    # ------------------------
    # Lesson Progress Endpoints
    # ------------------------
    path("progress/", LessonProgressListView.as_view()),
    
    # ------------------------
    # Course Endpoints
    # ------------------------
    path('', CourseListView.as_view()),
    path('<slug:slug>/', CourseDetailView.as_view()),
    
    # ------------------------
    # Course Quiz Endpoint
    # ------------------------
    path("<int:course_id>/quiz/", CourseQuizDetailView.as_view()),
]
