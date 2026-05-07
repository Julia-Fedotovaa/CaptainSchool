# apps/users/views.py  —  ПОЛНЫЙ ФАЙЛ (заменить существующий)
import json
from datetime import timedelta, date

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Avg
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.common.mixins import RoleRequiredMixin
from apps.education.models import Course, CourseCategory
from apps.users.forms import LoginForm, RegisterForm, UserEditForm, StudentProfileForm, MentorProfileForm, ParentProfileForm
from apps.users.models import User


# ─────────────────────────────────────────────────────────
#  HELPER: редирект в нужный кабинет по роли
# ─────────────────────────────────────────────────────────
def redirect_by_role(user, check_placement=False):
    role = user.role
    if role == User.Role.ADMIN:
        return redirect("admin_dashboard")
    if role == User.Role.MENTOR:
        return redirect("mentor_dashboard")
    if role == User.Role.PARENT:
        return redirect("parent_dashboard")
    # Student: если только что зарегистрировался — проверяем вступительный тест
    if check_placement:
        from apps.education.models import PlacementTestSession
        from apps.students.models import Student
        try:
            student = Student.objects.get(user=user)
            has_done = PlacementTestSession.objects.filter(
                student=student,
                status=PlacementTestSession.STATUS_COMPLETED,
            ).exists()
            if not has_done:
                return redirect("placement_test_start")
        except Student.DoesNotExist:
            pass
    return redirect("student_dashboard")


# ─────────────────────────────────────────────────────────
#  ЛОГИН
# ─────────────────────────────────────────────────────────
class UserLoginView(LoginView):
    template_name      = "users/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        # Если есть ?next= — используем его, иначе по роли
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
        return redirect_by_role(self.request.user).url  # нет .url у redirect()

    def form_valid(self, form):
        """После успешного логина редиректим по роли."""
        from django.contrib.auth import login as auth_login
        auth_login(self.request, form.get_user())
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect_by_role(form.get_user())


# ─────────────────────────────────────────────────────────
#  РЕГИСТРАЦИЯ
# ─────────────────────────────────────────────────────────
class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect_by_role(request.user)
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Профиль создаётся автоматически через post_save сигнал
            login(request, user)
            return redirect_by_role(user, check_placement=True)
        return render(request, self.template_name, {"form": form})


# ─────────────────────────────────────────────────────────
#  ЛОГАУТ
# ─────────────────────────────────────────────────────────
class UserLogoutView(View):
    http_method_names = ["post", "get"]

    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect(reverse("home"))

    def get(self, request):
        from django.contrib.auth import logout
        logout(request)
        return redirect(reverse("home"))



# ─────────────────────────────────────────────────────────
#  DASHBOARDS
# ─────────────────────────────────────────────────────────
class HomeRedirectView(RoleRequiredMixin, TemplateView):
    template_name = "users/home_redirect.html"
    allowed_roles = (User.Role.STUDENT, User.Role.PARENT, User.Role.MENTOR, User.Role.ADMIN)

    def get(self, request, *args, **kwargs):
        return redirect_by_role(request.user)


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    template_name  = "users/admin_dashboard.html"
    allowed_roles  = (User.Role.ADMIN,)


class ParentDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "users/parent_dashboard.html"
    allowed_roles = (User.Role.PARENT,)

    def get_context_data(self, **kwargs):
        from apps.students.models import Parent, Student, StudentStats, StudentBadge
        from apps.education.models import Enrollment, Schedule
        from apps.progress.models import Progress
        from django.db.models import Q
        from datetime import timedelta

        ctx = super().get_context_data(**kwargs)
        parent = get_object_or_404(Parent, user=self.request.user)

        children_data = []
        for student in parent.students.all().select_related("user"):
            # Статистика
            stats, _ = StudentStats.objects.get_or_create(student=student)

            # Достижения (все)
            badges = (
                StudentBadge.objects
                .filter(student=student)
                .select_related("badge")
                .order_by("awarded_at")
            )

            # Курсы с прогрессом
            enrollments = list(
                Enrollment.objects.filter(student=student).select_related("course", "course__category")
            )
            progress_map = {
                p.course_id: p.completion_percent
                for p in Progress.objects.filter(student=student)
            }
            for e in enrollments:
                e.progress_percent = progress_map.get(e.course_id, 0)
                e.lessons_count = e.course.lessons.count()

            all_percents = list(progress_map.values())
            avg = round(sum(all_percents) / len(all_percents)) if all_percents else 0

            # Вебинары ребёнка (ближайшие 30 дней)
            today = date.today()
            course_ids = [e.course_id for e in enrollments]
            webinars = (
                Schedule.objects
                .filter(
                    Q(students=student) | Q(course_id__in=course_ids),
                    date__gte=today,
                    date__lte=today + timedelta(days=30),
                )
                .select_related("course", "mentor", "mentor__user")
                .distinct()
                .order_by("date", "start_time")[:5]
            )

            # Даты для JS-календаря
            webinar_dates = [str(w.date) for w in webinars]

            children_data.append({
                "student": student,
                "stats": stats,
                "badges": badges,
                "enrollments": enrollments,
                "avg_completion": avg,
                "webinars": webinars,
                "webinar_dates_json": json.dumps(webinar_dates),
            })

        ctx["children"] = children_data
        return ctx


class MentorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "users/mentor_dashboard.html"
    allowed_roles = (User.Role.MENTOR,)

    def get_context_data(self, **kwargs):
        from apps.education.models import Course, Schedule, Enrollment, OpenAnswerSubmission, LessonProgress
        from apps.mentors.models import Mentor

        ctx = super().get_context_data(**kwargs)
        mentor = get_object_or_404(Mentor, user=self.request.user)

        # Только курсы этого ментора
        courses = mentor.courses.prefetch_related("enrollment_set").select_related("category").all()

        # Вебинары ментора — ближайшие 30 дней
        today = date.today()
        webinars = (
            Schedule.objects
            .filter(mentor=mentor, date__gte=today, date__lte=today + timedelta(days=30))
            .select_related("course", "course__category")
            .order_by("date", "start_time")
        )

        # Даты вебинаров для JS-календаря
        webinar_dates = list(webinars.values_list("date", flat=True))
        webinar_dates_json = json.dumps([str(d) for d in webinar_dates])

        # Вебинары на этой неделе
        week_end = today + timedelta(days=7)
        upcoming_count = webinars.filter(date__lte=week_end).count()

        # Всего учеников по курсам ментора
        total_students = Enrollment.objects.filter(course__in=courses).values("student").distinct().count()

        # Все курсы для возможности подписки
        all_courses = Course.objects.select_related("category").all()
        my_course_ids = set(courses.values_list("id", flat=True))

        # Развёрнутые ответы, ожидающие проверки по курсам этого ментора
        pending_subs = (
            OpenAnswerSubmission.objects
            .filter(lesson__course__mentors=mentor,
                    status=OpenAnswerSubmission.STATUS_PENDING)
            .select_related("student__user", "lesson", "card")
            .order_by("submitted_at")
        )
        # Группируем по (lesson, student)
        pending_reviews = {}
        for sub in pending_subs:
            key = (sub.lesson_id, sub.student_id)
            if key not in pending_reviews:
                pending_reviews[key] = {
                    "lesson":  sub.lesson,
                    "student": sub.student,
                    "subs":    [],
                }
            pending_reviews[key]["subs"].append(sub)
        pending_reviews = list(pending_reviews.values())

        ctx.update({
            "mentor": mentor,
            "courses": courses,
            "all_courses": all_courses,
            "my_course_ids": my_course_ids,
            "webinars": webinars[:10],
            "webinar_dates": webinar_dates_json,
            "total_courses": courses.count(),
            "total_students": total_students,
            "upcoming_webinars_count": upcoming_count,
            "pending_reviews": pending_reviews,
        })
        return ctx


class StudentDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "users/student_dashboard.html"
    allowed_roles = (User.Role.STUDENT,)

    def get_context_data(self, **kwargs):
        from apps.students.models import Student, StudentStats, StudentBadge
        from apps.education.models import Enrollment, Schedule, PlacementTestSession
        from apps.progress.models import Progress

        ctx = super().get_context_data(**kwargs)
        student = get_object_or_404(Student, user=self.request.user)

        enrollments = list(
            Enrollment.objects.filter(student=student).select_related("course", "course__category")
        )
        progress_map = {
            p.course_id: p.completion_percent
            for p in Progress.objects.filter(student=student)
        }
        for e in enrollments:
            e.progress_percent = progress_map.get(e.course_id, 0)
            e.lessons_count = e.course.lessons.count()

        all_percents   = list(progress_map.values())
        avg_completion = round(sum(all_percents) / len(all_percents)) if all_percents else 0

        stats, _ = StudentStats.objects.get_or_create(student=student)
        badges   = (
            StudentBadge.objects
            .filter(student=student)
            .select_related("badge")
            .order_by("awarded_at")
        )

        # Предстоящие вебинары: назначенные лично ИЛИ по курсам ученика
        from django.db.models import Q
        course_ids = [e.course_id for e in enrollments]
        from datetime import timedelta
        today = date.today()
        upcoming_webinars = (
            Schedule.objects
            .filter(
                Q(students=student) | Q(course_id__in=course_ids),
                date__gte=today,
                date__lte=today + timedelta(days=60),
            )
            .select_related("course", "course__category", "mentor", "mentor__user")
            .distinct()
            .order_by("date", "start_time")[:10]
        )
        webinar_dates = list(upcoming_webinars.values_list("date", flat=True))
        webinar_dates_json = json.dumps([str(d) for d in webinar_dates])

        placement_done = PlacementTestSession.objects.filter(
            student=student,
            status=PlacementTestSession.STATUS_COMPLETED,
        ).exists()

        ctx.update({
            "student":            student,
            "enrollments":        enrollments,
            "avg_completion":     avg_completion,
            "stats":              stats,
            "badges":             badges,
            "upcoming_webinars":  upcoming_webinars,
            "webinar_dates":      webinar_dates_json,
            "placement_done":     placement_done,
        })
        return ctx


# ─────────────────────────────────────────────────────────
#  РЕДАКТИРОВАНИЕ ПРОФИЛЯ
# ─────────────────────────────────────────────────────────
class ProfileEditView(RoleRequiredMixin, View):
    template_name = "users/profile_edit.html"
    allowed_roles = (User.Role.STUDENT, User.Role.PARENT, User.Role.MENTOR)

    def _get_profile_form_class(self, role):
        if role == User.Role.STUDENT:
            return StudentProfileForm
        elif role == User.Role.MENTOR:
            return MentorProfileForm
        elif role == User.Role.PARENT:
            return ParentProfileForm
        return None

    def _get_profile_instance(self, user):
        if user.role == User.Role.STUDENT:
            from apps.students.models import Student
            return Student.objects.filter(user=user).first()
        elif user.role == User.Role.MENTOR:
            from apps.mentors.models import Mentor
            return Mentor.objects.filter(user=user).first()
        elif user.role == User.Role.PARENT:
            from apps.students.models import Parent
            return Parent.objects.filter(user=user).first()
        return None

    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        ProfileForm = self._get_profile_form_class(request.user.role)
        profile_form = ProfileForm(instance=self._get_profile_instance(request.user)) if ProfileForm else None
        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form,
        })

    def post(self, request):
        user_form = UserEditForm(request.POST, request.FILES, instance=request.user)
        ProfileForm = self._get_profile_form_class(request.user.role)
        profile_instance = self._get_profile_instance(request.user)
        profile_form = ProfileForm(request.POST, instance=profile_instance) if ProfileForm else None

        forms_valid = user_form.is_valid() and (profile_form is None or profile_form.is_valid())
        if forms_valid:
            user = user_form.save(commit=False)
            if request.POST.get("avatar_clear") == "1":
                if user.avatar:
                    user.avatar.delete(save=False)
                user.avatar = None
            user.save()
            if profile_form:
                profile_form.save()
            return redirect_by_role(request.user)

        return render(request, self.template_name, {
            "user_form": user_form,
            "profile_form": profile_form,
        })


# ─────────────────────────────────────────────────────────
#  СТАТИЧЕСКИЕ СТРАНИЦЫ
# ─────────────────────────────────────────────────────────
class AboutView(TemplateView):
    template_name = "pages/about.html"


class ServicesView(TemplateView):
    template_name = "pages/services.html"


class HelpView(TemplateView):
    template_name = "pages/help.html"


class FaqView(TemplateView):
    template_name = "pages/faq.html"


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"


class TermsView(TemplateView):
    template_name = "pages/terms.html"


# ─────────────────────────────────────────────────────────
#  ПУБЛИЧНЫЕ СТРАНИЦЫ
# ─────────────────────────────────────────────────────────
def home(request):
    courses = (
        Course.objects
        .annotate(review_count=Count("reviews"), avg_rating=Avg("reviews__rating"))
        .order_by("-review_count", "-avg_rating")[:3]
    )
    placeholders = ["course_web.png", "course_writing.png", "course_design.png"]
    for idx, course in enumerate(courses):
        course.placeholder = None if getattr(course, "image", None) else placeholders[idx % len(placeholders)]
    return render(request, "home.html", {"top_courses": courses})


def contact_submit(request):
    from apps.common.models import ContactMessage
    sent = False
    if request.method == "POST":
        name    = request.POST.get("name", "").strip()
        email   = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            sent = True

    # Рендерим home с флагом — не делаем redirect, чтобы показать зелёное сообщение
    courses = (
        Course.objects
        .annotate(review_count=Count("reviews"), avg_rating=Avg("reviews__rating"))
        .order_by("-review_count", "-avg_rating")[:3]
    )
    placeholders = ["course_web.png", "course_writing.png", "course_design.png"]
    for idx, course in enumerate(courses):
        course.placeholder = None if getattr(course, "image", None) else placeholders[idx % len(placeholders)]
    return render(request, "home.html", {"top_courses": courses, "contact_sent": sent})


def all_courses(request):
    from apps.education.models import Enrollment
    from apps.progress.models import Progress

    categories = CourseCategory.objects.all()
    courses = Course.objects.select_related("category").order_by("name")
    category_id = request.GET.get("category")
    if category_id:
        if category_id == "all":
            return redirect("all_courses")
        courses = courses.filter(category_id=category_id)

    courses = list(courses)
    enrolled_ids = set()
    progress_map = {}
    my_course_ids = set()  # для ментора
    children_enrolled_ids = set()
    children_enrolled_names = {}   # course_id → [child_name, ...]

    user = request.user
    if user.is_authenticated:
        if user.role == User.Role.STUDENT:
            from apps.students.models import Student
            student = Student.objects.filter(user=user).first()
            if student:
                enrolled_ids = set(
                    Enrollment.objects.filter(student=student).values_list("course_id", flat=True)
                )
                for p in Progress.objects.filter(student=student):
                    progress_map[p.course_id] = p.completion_percent

        elif user.role == User.Role.MENTOR:
            from apps.mentors.models import Mentor
            mentor = Mentor.objects.filter(user=user).first()
            if mentor:
                my_course_ids = set(mentor.courses.values_list("id", flat=True))

        elif user.role == User.Role.PARENT:
            from apps.students.models import Parent
            parent = Parent.objects.filter(user=user).first()
            if parent:
                # course_id → list of enrolled child names
                for s in parent.students.select_related("user").all():
                    for eid in Enrollment.objects.filter(student=s).values_list("course_id", flat=True):
                        children_enrolled_ids.add(eid)
                        children_enrolled_names.setdefault(eid, []).append(
                            s.user.get_full_name() or s.user.username
                        )

    for c in courses:
        c.is_enrolled = c.id in enrolled_ids
        c.progress_percent = progress_map.get(c.id, 0)
        c.is_my_course = c.id in my_course_ids
        c.child_enrolled = c.id in children_enrolled_ids
        c.enrolled_child_names = children_enrolled_names.get(c.id, [])
        c.lessons_count = c.lessons.count()

    # Pre-split into sections for clean template rendering
    enrolled_courses = [c for c in courses if c.is_enrolled]
    available_courses = [c for c in courses if not c.is_enrolled]
    my_courses = [c for c in courses if c.is_my_course]
    other_courses = [c for c in courses if not c.is_my_course]
    child_courses = [c for c in courses if c.child_enrolled]
    child_available = [c for c in courses if not c.child_enrolled]

    return render(request, "courses/all_courses.html", {
        "courses": courses,
        "enrolled_courses": enrolled_courses,
        "available_courses": available_courses,
        "my_courses": my_courses,
        "other_courses": other_courses,
        "child_courses": child_courses,
        "child_available": child_available,
        "categories": categories,
        "active_category": category_id,
    })