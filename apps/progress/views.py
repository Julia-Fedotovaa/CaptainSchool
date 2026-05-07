from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from apps.common.mixins import RoleRequiredMixin
from apps.users.models import User
from .models import Progress
from ..students.models import Student, Parent


class ProgressListView(RoleRequiredMixin, ListView):
    model = Progress
    template_name = "progress/progress_list.html"
    context_object_name = "items"
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class ProgressCreateView(RoleRequiredMixin, CreateView):
    model = Progress
    fields = ["student", "course", "completion_percent", "result"]
    template_name = "common/form.html"
    success_url = reverse_lazy("progress_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class ProgressUpdateView(RoleRequiredMixin, UpdateView):
    model = Progress
    fields = ["completion_percent", "result"]
    template_name = "common/form.html"
    success_url = reverse_lazy("progress_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class StudentProgressView(RoleRequiredMixin, ListView):
    model = Progress
    template_name = "progress/student_progress.html"
    context_object_name = "items"
    allowed_roles = (User.Role.STUDENT,)

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        print(student)
        return Progress.objects.filter(student=student)


class ParentChildProgressView(RoleRequiredMixin, ListView):
    model = Progress
    template_name = "progress/parent_child_progress.html"
    context_object_name = "items"
    allowed_roles = (User.Role.PARENT,)

    def get_queryset(self):
        parent = get_object_or_404(Parent, user=self.request.user)
        student = get_object_or_404(
            Student,
            id=self.kwargs["student_id"],
            parents=parent
        )
        return Progress.objects.filter(student=student)
