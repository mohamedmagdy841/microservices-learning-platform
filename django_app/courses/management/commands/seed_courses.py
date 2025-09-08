from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from courses.models import Category, Course, Enrollment, Module, Lesson, LessonProgress

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with fake categories, courses, modules, lessons, enrollments, and progress"

    def add_arguments(self, parser):
        parser.add_argument("--categories", type=int, default=3)
        parser.add_argument("--courses", type=int, default=5)
        parser.add_argument("--modules", type=int, default=4)
        parser.add_argument("--lessons", type=int, default=5)

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding data..."))

        # ✅ Use only existing users with role=2
        students = User.objects.filter(role=2)
        if not students.exists():
            self.stdout.write(self.style.ERROR("⚠️ No users with role=2 found. Aborting."))
            return

        # Create Categories
        categories = []
        for _ in range(options["categories"]):
            cat = Category.objects.create(
                name=fake.unique.word().title(),
                description=fake.text(max_nb_chars=100)
            )
            categories.append(cat)

        # Create Courses, Modules, Lessons
        for _ in range(options["courses"]):
            course = Course.objects.create(
                category=random.choice(categories),
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=200),
                is_published=True,
            )

            for m in range(1, options["modules"] + 1):
                module = Module.objects.create(
                    course=course,
                    title=f"Module {m}: {fake.word().title()}",
                    order_index=m,
                )

                for l in range(1, options["lessons"] + 1):
                    Lesson.objects.create(
                        module=module,
                        title=f"Lesson {l}: {fake.sentence(nb_words=3)}",
                        video_url=fake.url(),
                        order_index=l,
                    )

        # Enroll students into random courses
        for student in students:
            courses_to_enroll = random.sample(list(Course.objects.all()), k=min(3, Course.objects.count()))
            for course in courses_to_enroll:
                enrollment, _ = Enrollment.objects.get_or_create(user=student, course=course)

                # Add lesson progress
                lessons = Lesson.objects.filter(module__course=course)
                for lesson in lessons:
                    LessonProgress.objects.create(
                        enrollment=enrollment,
                        lesson=lesson,
                        progress=Decimal(str(random.choice([0, 25, 50, 75, 100])))
                    )

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed!"))

# python manage.py seed_courses --categories 3 --courses 5 --modules 3 --lessons 4
