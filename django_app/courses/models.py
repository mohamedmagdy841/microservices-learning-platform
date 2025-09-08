from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

from backend.utils import (
    HashedUploadPath,
    validate_image_extension,
    validate_image_size
)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
 
class Course(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment', related_name="enrolled_courses")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    thumbnail = models.ImageField(
        upload_to=HashedUploadPath('courses/'),
        validators=[validate_image_extension, validate_image_size],
        blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'course')
        
    def __str__(self):
        return f"{self.user} enrolled in {self.course}"
        
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order_index = models.PositiveIntegerField()

    class Meta:
        ordering = ["order_index"]
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    order_index = models.PositiveIntegerField()

    class Meta:
        ordering = ["order_index"]

    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress_records")
    progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ('enrollment', 'lesson')
    
    @property
    def is_completed(self):
        return self.progress >= Decimal("100.00")

    def __str__(self):
        status = "completed" if self.is_completed else f"{self.progress}% done"
        return f"{self.enrollment.user} - {self.lesson}: {status}"
