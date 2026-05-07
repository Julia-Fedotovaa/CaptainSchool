from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from apps.common.mixins import RoleRequiredMixin
from apps.users.models import User
from .models import IndividualTrajectory, TrajectoryCourse
from ..students.models import Student, Parent


class TrajectoryListView(RoleRequiredMixin, ListView):
    model = IndividualTrajectory
    template_name = "trajectories/trajectory_list.html"
    context_object_name = "items"
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class TrajectoryCreateView(RoleRequiredMixin, CreateView):
    model = IndividualTrajectory
    fields = ["student", "track", "start_date", "status", "goals"]
    template_name = "common/form.html"
    success_url = reverse_lazy("trajectory_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class TrajectoryUpdateView(RoleRequiredMixin, UpdateView):
    model = IndividualTrajectory
    fields = ["status", "goals"]
    template_name = "common/form.html"
    success_url = reverse_lazy("trajectory_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class StudentTrajectoryView(RoleRequiredMixin, ListView):
    model = IndividualTrajectory
    template_name = "trajectories/student_trajectory.html"
    context_object_name = "items"
    allowed_roles = (User.Role.STUDENT,)

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        return IndividualTrajectory.objects.filter(student=student)


class ParentChildTrajectoryView(RoleRequiredMixin, ListView):
    model = IndividualTrajectory
    template_name = "trajectories/parent_child_trajectory.html"
    context_object_name = "items"
    allowed_roles = (User.Role.PARENT,)

    def get_queryset(self):
        parent = get_object_or_404(Parent, user=self.request.user)
        student = get_object_or_404(
            Student,
            id=self.kwargs["student_id"],
            parents=parent
        )
        return IndividualTrajectory.objects.filter(student=student)


class GenerateTrajectoryView(LoginRequiredMixin, View):
    """Генерирует траекторию из результатов placement test."""

    def post(self, request):
        from apps.education.models import PlacementTestSession, Course, Enrollment, Track, CourseCategory

        session_id = request.POST.get("session_id")
        category_id = request.POST.get("category_id")

        student = get_object_or_404(Student, user=request.user)
        session = get_object_or_404(
            PlacementTestSession, id=session_id, student=student
        )
        category = get_object_or_404(CourseCategory, id=category_id)

        # Находим курсы в выбранной категории
        courses = list(Course.objects.filter(category=category).order_by("id"))

        # Находим или создаём трек для категории
        track, _ = Track.objects.get_or_create(
            name=f"Траектория: {category.name}",
            defaults={
                "description": f"Автоматически сгенерированный трек для категории «{category.name}»",
                "format": "Онлайн",
                "difficulty": "Адаптивный",
            }
        )

        # Создаём траекторию
        trajectory, created = IndividualTrajectory.objects.get_or_create(
            student=student,
            track=track,
            defaults={
                "category": category,
                "start_date": date.today(),
                "status": "Активна",
                "goals": f"Обучение по направлению «{category.name}»",
            }
        )

        if created:
            # Добавляем курсы в траекторию и записываем ученика
            for idx, course in enumerate(courses):
                TrajectoryCourse.objects.get_or_create(
                    trajectory=trajectory,
                    course=course,
                    defaults={"order": idx}
                )
                Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                )

        return render(request, "trajectories/generating.html", {
            "trajectory": trajectory,
            "category": category,
            "courses_count": len(courses),
        })
