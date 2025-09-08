from .pagination import CustomPagination
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView
)
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer
)
from .models import (
    Course
)


class CourseListView(ListAPIView):
    serializer_class = CourseListSerializer
    pagination_class = CustomPagination
    queryset = (
        Course.objects.
        select_related("category").
        prefetch_related("modules", "enrollments")
    )

class CourseDetailView(RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    queryset = (
        Course.objects.
        select_related("category").
        prefetch_related("modules", "modules__lessons")
    )
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    
