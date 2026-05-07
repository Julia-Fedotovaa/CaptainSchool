import json
import secrets
import string
from datetime import date

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView

from apps.common.mixins import RoleRequiredMixin
from apps.users.models import User
from apps.users.forms import StudentProfileForm
from .models import Parent, Student
from apps.education.models import Enrollment, Schedule


class ParentChildrenListView(RoleRequiredMixin, ListView):
    template_name = "students/parent_children.html"
    context_object_name = "children"
    allowed_roles = (User.Role.PARENT,)

    def get_queryset(self):
        parent = get_object_or_404(Parent, user=self.request.user)
        return parent.students.all()


class ParentChildCoursesView(RoleRequiredMixin, ListView):
    template_name = "students/parent_child_courses.html"
    context_object_name = "enrollments"
    allowed_roles = (User.Role.PARENT,)

    def get_queryset(self):
        parent = get_object_or_404(Parent, user=self.request.user)
        student = get_object_or_404(
            Student,
            user_id=self.kwargs["student_id"],
            parents=parent
        )
        return Enrollment.objects.filter(student=student)


class ParentChildScheduleView(RoleRequiredMixin, ListView):
    template_name = "students/parent_child_schedule.html"
    context_object_name = "items"
    allowed_roles = (User.Role.PARENT,)

    def get_queryset(self):
        parent = get_object_or_404(Parent, user=self.request.user)
        student = get_object_or_404(
            Student,
            user_id=self.kwargs["student_id"],
            parents=parent
        )

        course_ids = Enrollment.objects.filter(
            student=student
        ).values_list("course_id", flat=True)

        return Schedule.objects.filter(course_id__in=course_ids)


def _generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def _generate_username(first_name, last_name):
    """Generate a unique username from name via transliteration."""
    raw = f"{first_name}_{last_name}".lower()
    base = "".join(_TRANSLIT.get(ch, ch) for ch in raw)
    # Keep only ASCII letters, digits, underscore
    base = "".join(ch for ch in base if ch.isascii() and (ch.isalnum() or ch == "_"))
    base = base[:30] or "student"
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1
    return username


class AddChildView(RoleRequiredMixin, View):
    """POST: создать ребёнка и привязать к родителю."""
    allowed_roles = (User.Role.PARENT,)

    def post(self, request):
        parent = get_object_or_404(Parent, user=request.user)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        birth_date = data.get("birth_date", "")
        education_level = data.get("education_level", "").strip()

        if not first_name or not last_name:
            return JsonResponse(
                {"ok": False, "error": "Имя и фамилия обязательны"}, status=400
            )

        password = _generate_password()
        username = _generate_username(first_name, last_name)
        email = f"{username}@child.eduplatform.local"

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.Role.STUDENT,
        )

        try:
            bd = date.fromisoformat(birth_date) if birth_date else date(2010, 1, 1)
        except (ValueError, TypeError):
            bd = date(2010, 1, 1)

        # Signal auto-creates Student; update it with actual data
        student = Student.objects.get(user=user)
        student.birth_date = bd
        student.education_level = education_level or "Начальная школа"
        student.study_status = "Активен"
        student.initial_password = password
        student.save()

        parent.students.add(student)

        return JsonResponse({
            "ok": True,
            "child": {
                "id": user.pk,
                "name": user.get_full_name(),
                "username": username,
                "password": password,
            },
        })


class ParentChildEditView(RoleRequiredMixin, View):
    """Родитель редактирует профиль ребёнка."""
    allowed_roles = (User.Role.PARENT,)
    template_name = "students/parent_child_edit.html"

    def _get_child(self, request, student_id):
        parent = get_object_or_404(Parent, user=request.user)
        return get_object_or_404(Student, user_id=student_id, parents=parent)

    def get(self, request, student_id):
        student = self._get_child(request, student_id)
        from django import forms

        class ChildUserForm(forms.ModelForm):
            class Meta:
                model = User
                fields = ["first_name", "last_name"]
                widgets = {
                    "first_name": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Имя"}),
                    "last_name": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Фамилия"}),
                }
                labels = {"first_name": "Имя", "last_name": "Фамилия"}

        user_form = ChildUserForm(instance=student.user)
        profile_form = StudentProfileForm(instance=student)
        return render(request, self.template_name, {
            "student": student,
            "user_form": user_form,
            "profile_form": profile_form,
        })

    def post(self, request, student_id):
        student = self._get_child(request, student_id)
        from django import forms

        class ChildUserForm(forms.ModelForm):
            class Meta:
                model = User
                fields = ["first_name", "last_name"]
                widgets = {
                    "first_name": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Имя"}),
                    "last_name": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Фамилия"}),
                }
                labels = {"first_name": "Имя", "last_name": "Фамилия"}

        user_form = ChildUserForm(request.POST, instance=student.user)
        profile_form = StudentProfileForm(request.POST, instance=student)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("parent_dashboard")

        return render(request, self.template_name, {
            "student": student,
            "user_form": user_form,
            "profile_form": profile_form,
        })


class ChildCredentialsView(RoleRequiredMixin, View):
    """GET: показать логин/пароль ребёнка."""
    allowed_roles = (User.Role.PARENT,)

    def get(self, request, student_id):
        parent = get_object_or_404(Parent, user=request.user)
        student = get_object_or_404(
            Student,
            user_id=student_id,
            parents=parent,
        )
        return JsonResponse({
            "ok": True,
            "username": student.user.username,
            "password": student.initial_password or "—",
            "name": student.user.get_full_name(),
        })
