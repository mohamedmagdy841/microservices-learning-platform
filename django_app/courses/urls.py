from django.urls import path
from .views import (
    CourseListView,
    CourseDetailView,
    CategoryListView,
    CategoryDetailView,
    EnrollmentListView,
    LessonProgressListView
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
    path("enrollments/", EnrollmentListView.as_view()),

    # ------------------------
    # Lesson Progress Endpoints
    # ------------------------
    path("progress/", LessonProgressListView.as_view()),
    
    # ------------------------
    # Course Endpoints
    # ------------------------
    path('', CourseListView.as_view()),
    path('<slug:slug>/', CourseDetailView.as_view()),
]
