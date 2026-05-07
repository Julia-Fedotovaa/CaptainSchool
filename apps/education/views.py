import json
import random
from datetime import timezone, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from apps.common.mixins import RoleRequiredMixin, FormTitleMixin
from apps.users.models import User
from .models import Track, Course, Schedule, Enrollment, PlacementTest, PlacementTestSession, PlacementQuestion, \
    PlacementAnswer, ChoiceOption
from ..students.models import Student


# ---------- ADMIN: Tracks ----------
class TrackListView(RoleRequiredMixin, ListView):
    model = Track
    template_name = "education/track_list.html"
    context_object_name = "tracks"
    allowed_roles = (User.Role.ADMIN,)


class TrackCreateView(RoleRequiredMixin, FormTitleMixin, CreateView):
    model = Track
    fields = ["name", "description", "format", "difficulty"]
    template_name = "common/form.html"
    success_url = reverse_lazy("track_list")
    allowed_roles = (User.Role.ADMIN,)
    form_title_create = "Создание трека"


class TrackUpdateView(RoleRequiredMixin, FormTitleMixin, UpdateView):
    model = Track
    fields = ["name", "description", "format", "difficulty"]
    template_name = "common/form.html"
    success_url = reverse_lazy("track_list")
    allowed_roles = (User.Role.ADMIN,)
    form_title_update = "Редактирование трека"


class TrackDeleteView(RoleRequiredMixin, DeleteView):
    model = Track
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("track_list")
    allowed_roles = (User.Role.ADMIN,)


# ---------- ADMIN + MENTOR: Courses ----------
class CourseListView(RoleRequiredMixin, ListView):
    model = Course
    template_name = "education/course_list.html"
    context_object_name = "courses"
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class CourseCreateView(RoleRequiredMixin, FormTitleMixin, CreateView):
    model = Course
    fields = ["track", "name", "description", "category", "image", "format", "duration_hours"]
    template_name = "common/form.html"
    success_url = reverse_lazy("course_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)
    form_title_create = "Создание курса"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.role == User.Role.MENTOR:
            from apps.mentors.models import Mentor
            mentor = Mentor.objects.filter(user=self.request.user).first()
            if mentor:
                self.object.mentors.add(mentor)
        return response


class CourseUpdateView(RoleRequiredMixin, FormTitleMixin, UpdateView):
    model = Course
    fields = ["track", "name", "description", "category", "image", "format", "duration_hours"]
    template_name = "common/form.html"
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)
    form_title_update = "Редактирование курса"

    def get_success_url(self):
        if self.request.user.role == User.Role.MENTOR:
            return reverse("mentor_dashboard")
        return reverse("course_list")


class CourseDeleteView(RoleRequiredMixin, DeleteView):
    model = Course
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get_success_url(self):
        if self.request.user.role == User.Role.MENTOR:
            return reverse("mentor_dashboard")
        return reverse("course_list")

    def get(self, request, *args, **kwargs):
        # Skip confirmation page — delete via POST only (modal handles confirmation)
        return redirect("mentor_dashboard")

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


# ---------- ADMIN + MENTOR: Schedule ----------
class ScheduleListView(RoleRequiredMixin, ListView):
    model = Schedule
    template_name = "education/schedule_list.html"
    context_object_name = "items"
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


class ScheduleCreateView(RoleRequiredMixin, CreateView):
    model = Schedule
    fields = ["course", "date", "start_time", "end_time", "lesson_format", "location", "description"]
    template_name = "education/schedule_form.html"
    success_url = reverse_lazy("schedule_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.role == User.Role.MENTOR:
            from apps.mentors.models import Mentor
            mentor = Mentor.objects.filter(user=self.request.user).first()
            if mentor:
                form.fields["course"].queryset = mentor.courses.all()
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Назначить вебинар"
        ctx["submit_label"] = "Создать вебинар"
        ctx["assigned_students"] = []
        return ctx

    def form_valid(self, form):
        if self.request.user.role == User.Role.MENTOR:
            from apps.mentors.models import Mentor
            mentor = Mentor.objects.filter(user=self.request.user).first()
            if mentor:
                form.instance.mentor = mentor
        response = super().form_valid(form)
        # Назначаем учеников из скрытого поля
        student_ids = self.request.POST.get("student_ids", "")
        if student_ids:
            ids = [int(x) for x in student_ids.split(",") if x.strip().isdigit()]
            students = Student.objects.filter(user_id__in=ids)
            self.object.students.set(students)
        return response


class ScheduleUpdateView(RoleRequiredMixin, UpdateView):
    model = Schedule
    fields = ["course", "date", "start_time", "end_time", "lesson_format", "location", "description"]
    template_name = "education/schedule_form.html"
    success_url = reverse_lazy("schedule_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.role == User.Role.MENTOR:
            from apps.mentors.models import Mentor
            mentor = Mentor.objects.filter(user=self.request.user).first()
            if mentor:
                form.fields["course"].queryset = mentor.courses.all()
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Редактировать вебинар"
        ctx["submit_label"] = "Сохранить изменения"
        ctx["assigned_students"] = [
            {"id": s.user_id, "name": s.user.get_full_name() or s.user.email}
            for s in self.object.students.select_related("user")
        ]
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        student_ids = self.request.POST.get("student_ids", "")
        if student_ids:
            ids = [int(x) for x in student_ids.split(",") if x.strip().isdigit()]
            students = Student.objects.filter(user_id__in=ids)
            self.object.students.set(students)
        else:
            self.object.students.clear()
        return response


class ScheduleDeleteView(RoleRequiredMixin, DeleteView):
    model = Schedule
    template_name = "common/confirm_delete.html"
    success_url = reverse_lazy("schedule_list")
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)


# ---------- STUDENT: view-only ----------
class StudentCourseListView(RoleRequiredMixin, ListView):
    model = Course
    template_name = "education/student_courses.html"
    context_object_name = "courses"
    allowed_roles = (User.Role.STUDENT,)


class StudentScheduleListView(RoleRequiredMixin, ListView):
    model = Schedule
    template_name = "education/student_schedule.html"
    context_object_name = "items"
    allowed_roles = (User.Role.STUDENT,)

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        course_ids = Enrollment.objects.filter(
            student=student
        ).values_list("course_id", flat=True)

        return Schedule.objects.filter(course_id__in=course_ids)



# ---------- PARENT: view child's schedule (упрощение) ----------
class ParentChildScheduleView(RoleRequiredMixin, ListView):
    model = Schedule
    template_name = "education/parent_child_schedule.html"
    context_object_name = "items"
    allowed_roles = (User.Role.PARENT,)


class AvailableCourseListView(RoleRequiredMixin, ListView):
    model = Course
    template_name = "education/available_courses.html"
    context_object_name = "courses"
    allowed_roles = (User.Role.STUDENT,)

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        enrolled_ids = Enrollment.objects.filter(
            student=student
        ).values_list("course_id", flat=True)

        return Course.objects.exclude(id__in=enrolled_ids)


class MyCourseListView(RoleRequiredMixin, ListView):
    model = Enrollment
    template_name = "education/my_courses.html"
    context_object_name = "enrollments"
    allowed_roles = (User.Role.STUDENT,)

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        return Enrollment.objects.filter(student=student)


class EnrollCourseView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Role.STUDENT,)

    def get(self, request, course_id):
        student = get_object_or_404(Student, user=request.user)
        course = get_object_or_404(Course, id=course_id)

        Enrollment.objects.get_or_create(
            student=student,
            course=course
        )
        return redirect("my_courses")


class UnenrollCourseView(RoleRequiredMixin, ListView):
    allowed_roles = (User.Role.STUDENT,)

    def get(self, request, course_id):
        student = get_object_or_404(Student, user=request.user)
        Enrollment.objects.filter(
            student=student,
            course_id=course_id
        ).delete()
        return redirect("my_courses")


def ability_test(request):
    if request.method == "POST":
        # Здесь мы будем обрабатывать результаты после нажатия "Завершить"
        # request.POST будет содержать ответы пользователя
        # print(request.POST)
        return render(request, "education/test_result.html")  # Заглушка страницы результатов

    return render(request, "education/ability_test.html")


class PlacementTestView(LoginRequiredMixin, View):

    def _get_or_create_session(self, request):
        test = get_object_or_404(PlacementTest, is_active=True)
        student = get_object_or_404(Student, user=request.user)
        session = PlacementTestSession.objects.filter(
            student=student, test=test,
            status=PlacementTestSession.STATUS_IN_PROGRESS
        ).first()
        if not session:
            session = PlacementTestSession.objects.create(
                student=student, test=test,
                current_question_index=0,
                category_scores={}
            )
        return session

    def get(self, request):
        session = self._get_or_create_session(request)
        questions = list(session.test.questions_ordered())
        total = len(questions)

        if session.current_question_index >= total:
            return redirect("placement_test_result", session_id=session.id)

        question = questions[session.current_question_index]

        pairs_with_shuffled = None
        if question.question_type == PlacementQuestion.TYPE_MATCHING:
            pairs = list(question.pairs.all())
            right_shuffled = [p.right_text for p in pairs]
            random.shuffle(right_shuffled)
            pairs_with_shuffled = list(zip(pairs, right_shuffled))

        return render(request, "placement_test/test.html", {
            "test": session.test,
            "session": session,
            "question": question,
            "question_num": session.current_question_index + 1,
            "total": total,
            "pairs_with_shuffled": pairs_with_shuffled,
        })

    def post(self, request):
        session_id = request.POST.get("session_id")
        question_id = request.POST.get("question_id")

        session = get_object_or_404(
            PlacementTestSession, id=session_id,
            status=PlacementTestSession.STATUS_IN_PROGRESS
        )
        question = get_object_or_404(PlacementQuestion, id=question_id)

        answer, created = PlacementAnswer.objects.get_or_create(
            session=session, question=question
        )

        scores = session.category_scores or {}

        if created:
            if question.question_type == PlacementQuestion.TYPE_CHOICE:
                choice_id = request.POST.get("choice_id")
                if choice_id:
                    choice = get_object_or_404(ChoiceOption, id=choice_id, question=question)
                    answer.selected_choice = choice
                    answer.save()
                    # начисляем балл категории
                    if choice.category_id:
                        key = str(choice.category_id)
                        scores[key] = scores.get(key, 0) + 1

            elif question.question_type == PlacementQuestion.TYPE_MATCHING:
                try:
                    data = json.loads(request.POST.get("matching_answer", "{}"))
                except (json.JSONDecodeError, TypeError):
                    data = {}
                answer.matching_answer = data
                answer.save()

                # Для каждой правильно угаданной пары — балл её категории
                for pair in question.pairs.all():
                    if data.get(str(pair.id)) == pair.right_text and pair.category_id:
                        key = str(pair.category_id)
                        scores[key] = scores.get(key, 0) + 1

        # Сохраняем накопленные баллы
        session.category_scores = scores
        session.current_question_index = session.current_question_index + 1

        questions = list(session.test.questions_ordered())
        if session.current_question_index >= len(questions):
            session.status = PlacementTestSession.STATUS_COMPLETED
            session.finished_at = datetime.now(timezone.utc)
            session.save()

            # Обновляем StudentStats если модель существует
            try:
                from apps.students.models import StudentStats
                stats, _ = StudentStats.objects.get_or_create(student=session.student)
                stats.quizzes_passed += 1
                duration = int((session.finished_at - session.started_at).total_seconds())
                if stats.best_time_seconds is None or duration < stats.best_time_seconds:
                    stats.best_time_seconds = duration
                stats.save()
            except Exception:
                pass

            return redirect("placement_test_result", session_id=session.id)

        session.save()
        return redirect("placement_test_start")


class PlacementTestResultView(LoginRequiredMixin, View):

    def get(self, request, session_id):
        session = get_object_or_404(
            PlacementTestSession, id=session_id,
            student__user=request.user
        )

        # Топ-2 категории по баллам
        top_cats = session.top_categories(n=2)

        # Курсы из топ-категорий (до 3 на категорию)
        recommended_courses = []
        seen_ids = set()
        for cat, score in top_cats:
            courses = (
                Course.objects
                .filter(category=cat)
                .exclude(id__in=seen_ids)[:3]
            )
            for c in courses:
                seen_ids.add(c.id)
                recommended_courses.append((c, cat))

        return render(request, "placement_test/result.html", {
            "session": session,
            "top_cats": top_cats,
            "recommended_courses": recommended_courses,
        })


from django.utils import timezone as tz


class CourseDetailView(LoginRequiredMixin, View):
    """Страница курса: список уроков + статистика для подписанных."""

    def get(self, request, course_id):
        from .models import Lesson, LessonProgress
        from apps.progress.models import Progress

        course  = get_object_or_404(Course, id=course_id)
        lessons = list(course.lessons.order_by("order"))

        is_enrolled = False
        student     = None
        lesson_progress_map = {}
        course_progress     = None
        is_mentor_course    = False
        child_enrolled      = False

        user = request.user

        if user.is_authenticated:
            # Студент
            if user.role == User.Role.STUDENT:
                from apps.students.models import Student as SM
                student = SM.objects.filter(user=user).first()
                if student:
                    is_enrolled = Enrollment.objects.filter(student=student, course=course).exists()
                    if is_enrolled:
                        for lp in LessonProgress.objects.filter(student=student, lesson__in=lessons):
                            lesson_progress_map[lp.lesson_id] = lp
                        course_progress = Progress.objects.filter(student=student, course=course).first()

            # Ментор — проверяем, является ли курс «своим»
            elif user.role == User.Role.MENTOR:
                from apps.mentors.models import Mentor
                mentor = Mentor.objects.filter(user=user).first()
                if mentor:
                    is_mentor_course = course.mentors.filter(pk=mentor.pk).exists()

            # Родитель — проверяем, записан ли хотя бы один ребёнок
            elif user.role == User.Role.PARENT:
                from apps.students.models import Parent
                parent = Parent.objects.filter(user=user).first()
                if parent:
                    child_ids = parent.students.values_list("pk", flat=True)
                    child_enrolled = Enrollment.objects.filter(
                        student_id__in=child_ids, course=course
                    ).exists()

        for lesson in lessons:
            lesson.progress = lesson_progress_map.get(lesson.id)

        completed_count = sum(
            1 for lp in lesson_progress_map.values() if lp.status == "completed"
        )

        return render(request, "education/course_detail.html", {
            "course":            course,
            "lessons":           lessons,
            "is_enrolled":       is_enrolled,
            "student":           student,
            "course_progress":   course_progress,
            "completed_lessons": completed_count,
            "total_lessons":     len(lessons),
            "is_mentor_course":  is_mentor_course,
            "child_enrolled":    child_enrolled,
        })

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        action = request.POST.get("action")

        # Действие родителя — записать ребёнка
        if action == "enroll_child":
            if request.user.role == User.Role.PARENT:
                from apps.students.models import Parent
                parent = Parent.objects.filter(user=request.user).first()
                if parent:
                    for child in parent.students.all():
                        Enrollment.objects.get_or_create(student=child, course=course)
            return redirect("course_detail", course_id=course_id)

        # Действия ученика
        try:
            from apps.students.models import Student as SM
            student = get_object_or_404(SM, user=request.user)
        except Exception:
            return redirect("course_detail", course_id=course_id)

        if action == "enroll":
            Enrollment.objects.get_or_create(student=student, course=course)
        elif action == "unenroll":
            Enrollment.objects.filter(student=student, course=course).delete()

        return redirect("course_detail", course_id=course_id)


class LessonPlayerView(LoginRequiredMixin, View):
    """SPA-плеер урока. Все карточки передаются в шаблон, JS переключает их."""

    def _student(self, request):
        from apps.students.models import Student as SM
        return get_object_or_404(SM, user=request.user)

    def _lp(self, student, lesson):
        from .models import LessonProgress
        lp, created = LessonProgress.objects.get_or_create(
            student=student, lesson=lesson,
            defaults={
                "status":           LessonProgress.STATUS_IN_PROGRESS,
                "total_test_cards": lesson.cards.filter(card_type__in=["test", "matching", "open_answer"]).count(),
                "correct_answers":  0,
                "current_card_index": 0,
            }
        )
        # Если урок уже завершён — сбрасываем для повторного прохождения
        if not created and lp.status == LessonProgress.STATUS_COMPLETED:
            # Запоминаем предыдущий результат для comeback-достижения
            lp._prev_score         = lp.score_percent
            lp.status              = LessonProgress.STATUS_IN_PROGRESS
            lp.current_card_index  = 0
            lp.correct_answers     = 0
            lp.total_test_cards    = lesson.cards.filter(card_type__in=["test", "matching", "open_answer"]).count()
            lp.completed_at        = None
            lp.save()
        elif not created and lp.status == LessonProgress.STATUS_NOT_STARTED:
            lp.status = LessonProgress.STATUS_IN_PROGRESS
            lp.save()
        return lp

    def get(self, request, lesson_id):
        from .models import Lesson, LessonCard, CardChoice

        lesson  = get_object_or_404(Lesson, id=lesson_id)
        student = self._student(request)

        if not Enrollment.objects.filter(student=student, course=lesson.course).exists():
            return redirect("course_detail", course_id=lesson.course_id)

        lp    = self._lp(student, lesson)
        cards = list(lesson.cards_ordered().prefetch_related("choices"))

        # Сериализуем карточки в JSON для JS
        cards_json = []
        for c in cards:
            entry = {
                "id":      c.id,
                "type":    c.card_type,
                "title":   c.title,
                "content": c.content,
                "image":   c.image.url if c.image else None,
            }
            if c.card_type == "test":
                entry["choices"] = [
                    {"id": ch.id, "text": ch.text, "correct": ch.is_correct}
                    for ch in c.choices.all()
                ]
            elif c.card_type == "matching":
                all_choices = list(c.choices.all())
                import random as _rnd
                rights = [ch.match_text for ch in all_choices]
                _rnd.shuffle(rights)
                entry["pairs"] = [
                    {"id": ch.id, "left": ch.text, "right": ch.match_text}
                    for ch in all_choices
                ]
                entry["shuffled_rights"] = rights
            elif c.card_type == "open_answer":
                # Не передаём правильные ответы клиенту — проверка на сервере
                entry["open_answer"] = True
            else:
                entry["choices"] = []
            cards_json.append(entry)

        return render(request, "education/lesson_player.html", {
            "lesson":       lesson,
            "course":       lesson.course,
            "cards_data":   cards_json,  # Python list — json_script тег сериализует сам
            "start_index":  lp.current_card_index
            if lp.status != "completed" else 0,
            "total":        len(cards),
            "lp":           lp,
        })


class LessonCardSubmitView(LoginRequiredMixin, View):
    """AJAX endpoint: принимает ответ на карточку, обновляет прогресс."""

    def post(self, request, lesson_id):
        from .models import Lesson, LessonProgress, CardChoice

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "bad json"}, status=400)

        lesson  = get_object_or_404(Lesson, id=lesson_id)
        from apps.students.models import Student as SM
        student = get_object_or_404(SM, user=request.user)
        lp      = get_object_or_404(LessonProgress, student=student, lesson=lesson)

        card_index = data.get("card_index", 0)
        choice_id  = data.get("choice_id")
        is_last    = data.get("is_last", False)
        card_type  = data.get("card_type", "")

        is_correct = None

        if card_type == "matching":
            # matching_answer: { pair_id: selected_right_text, ... }
            matching_answer = data.get("matching_answer", {})
            if matching_answer and card_index >= lp.current_card_index:
                pairs = CardChoice.objects.filter(
                    id__in=[int(k) for k in matching_answer.keys()]
                )
                all_ok = True
                for pair in pairs:
                    user_right = matching_answer.get(str(pair.id), "")
                    if user_right.strip().lower() != pair.match_text.strip().lower():
                        all_ok = False
                        break
                is_correct = all_ok
                if is_correct:
                    lp.correct_answers = (lp.correct_answers or 0) + 1

        elif card_type == "open_answer":
            user_text = data.get("user_text", "").strip()
            if user_text and card_index >= lp.current_card_index:
                from .models import LessonCard
                cards_at_idx = list(lesson.cards_ordered())
                if card_index < len(cards_at_idx):
                    card_obj = cards_at_idx[card_index]
                    accepted = list(card_obj.choices.values_list("text", flat=True))
                    is_correct = _fuzzy_match(user_text, accepted)
                    if is_correct:
                        lp.correct_answers = (lp.correct_answers or 0) + 1

        elif choice_id:
            try:
                choice     = CardChoice.objects.get(id=choice_id)
                is_correct = choice.is_correct
                if is_correct and card_index >= lp.current_card_index:
                    lp.correct_answers = (lp.correct_answers or 0) + 1
            except CardChoice.DoesNotExist:
                pass

        # Двигаем индекс только вперёд
        if card_index >= lp.current_card_index:
            lp.current_card_index = card_index + 1

        if is_last:
            lp.status       = LessonProgress.STATUS_COMPLETED
            lp.completed_at = tz.now()
            lp.save()
            _update_course_progress(student, lesson.course)
            # Начисляем достижения
            new_badge_codes = []
            try:
                from apps.students.badges import check_and_award, award_comeback, check_course_achievements
                new_badge_codes = check_and_award(student, lesson.course, lesson_progress=lp)
                # Курсо-специфичные достижения
                new_badge_codes.extend(check_course_achievements(student, lesson.course))
                # Comeback: если была пересдача и оценка улучшилась
                prev = getattr(lp, '_prev_score', None)
                if prev is not None:
                    if award_comeback(student, lp, prev):
                        new_badge_codes.append("comeback")
            except Exception as e:
                pass  # не ломаем урок из-за ошибки в системе наград
            request.session["new_badge_codes"] = new_badge_codes
            return JsonResponse({"ok": True, "finished": True})

        lp.save()
        return JsonResponse({"ok": True, "finished": False, "is_correct": is_correct})


class LessonResultView(LoginRequiredMixin, View):

    def get(self, request, lesson_id):
        from .models import Lesson, LessonProgress

        lesson  = get_object_or_404(Lesson, id=lesson_id)
        from apps.students.models import Student as SM
        student = get_object_or_404(SM, user=request.user)
        lp      = get_object_or_404(LessonProgress, student=student, lesson=lesson)

        next_lesson = Lesson.objects.filter(
            course=lesson.course, order__gt=lesson.order
        ).order_by("order").first()

        # Загружаем значки полученные за этот урок (выданные только что)
        from apps.students.models import StudentBadge
        new_badge_codes = request.session.pop("new_badge_codes", [])
        if new_badge_codes:
            recent_badges = (
                StudentBadge.objects
                .filter(student=student, badge__name__in=new_badge_codes)
                .select_related("badge")
                .order_by("-awarded_at")
            )
        else:
            recent_badges = StudentBadge.objects.none()

        return render(request, "education/lesson_result.html", {
            "lesson":        lesson,
            "lp":            lp,
            "course":        lesson.course,
            "next_lesson":   next_lesson,
            "recent_badges": recent_badges,
        })


def _update_course_progress(student, course):
    from apps.progress.models import Progress
    from .models import LessonProgress
    lessons   = list(course.lessons.all())
    total     = len(lessons)
    if not total:
        return
    completed = LessonProgress.objects.filter(
        student=student, lesson__in=lessons, status=LessonProgress.STATUS_COMPLETED
    ).count()
    Progress.objects.update_or_create(
        student=student, course=course,
        defaults={"completion_percent": round(completed / total * 100),
                  "result": f"{completed}/{total} уроков"}
    )

class CourseReviewView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        from apps.students.models import Student as StudentModel
        course  = get_object_or_404(Course, id=course_id)
        student = get_object_or_404(StudentModel, user=request.user)
        rating  = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()
        from .models import CourseReview
        CourseReview.objects.update_or_create(
            course=course, student=student,
            defaults={"rating": rating, "comment": comment}
        )
        return redirect("course_detail", course_id=course_id)


def _fuzzy_match(user_text, accepted_list, max_distance=2):
    """Сравнение ответа ученика с допустимыми ответами. Без учёта регистра, с допуском мелких опечаток."""
    user_lower = user_text.strip().lower()
    for accepted in accepted_list:
        acc_lower = accepted.strip().lower()
        if user_lower == acc_lower:
            return True
        # Допуск мелких опечаток через расстояние Левенштейна
        if abs(len(user_lower) - len(acc_lower)) <= max_distance:
            if _levenshtein(user_lower, acc_lower) <= max_distance:
                return True
    return False


def _levenshtein(s1, s2):
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (0 if c1 == c2 else 1)
            ))
        prev = curr
    return prev[-1]


def _save_cards(card_owner, cards_list):
    """Общая логика сохранения карточек (theory/test/matching/open_answer)."""
    from .models import LessonCard, CardChoice
    card_owner.cards.all().delete()
    for idx, card_data in enumerate(cards_list):
        card_type = card_data.get("type", "theory")
        card = LessonCard.objects.create(
            lesson=card_owner,
            card_type=card_type,
            order=idx,
            title=card_data.get("title", ""),
            content=card_data.get("content", ""),
        )
        if card_type == "test":
            for ch_idx, choice_data in enumerate(card_data.get("choices", [])):
                CardChoice.objects.create(
                    card=card,
                    text=choice_data.get("text", ""),
                    is_correct=choice_data.get("is_correct", False),
                    order=ch_idx,
                )
        elif card_type == "matching":
            for p_idx, pair in enumerate(card_data.get("pairs", [])):
                CardChoice.objects.create(
                    card=card,
                    text=pair.get("left", ""),
                    match_text=pair.get("right", ""),
                    order=p_idx,
                )
        elif card_type == "open_answer":
            for a_idx, ans in enumerate(card_data.get("accepted", [])):
                CardChoice.objects.create(
                    card=card,
                    text=ans if isinstance(ans, str) else str(ans),
                    order=a_idx,
                )


def _serialize_cards(cards_qs):
    """Сериализация карточек для редактора (JSON)."""
    result = []
    for c in cards_qs:
        entry = {
            "id": c.id,
            "type": c.card_type,
            "title": c.title,
            "content": c.content,
        }
        if c.card_type == "test":
            entry["choices"] = [
                {"id": ch.id, "text": ch.text, "is_correct": ch.is_correct}
                for ch in c.choices.all()
            ]
        elif c.card_type == "matching":
            entry["pairs"] = [
                {"left": ch.text, "right": ch.match_text}
                for ch in c.choices.all()
            ]
        elif c.card_type == "open_answer":
            entry["accepted"] = [ch.text for ch in c.choices.all()]
        else:
            entry["choices"] = []
        result.append(entry)
    return result


# ---------- MENTOR: Редактор урока (блочный) ----------
class LessonEditorView(RoleRequiredMixin, View):
    """GET — загружает редактор с данными урока. POST — сохраняет карточки из JSON."""
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get(self, request, lesson_id):
        from .models import Lesson, LESSON_COLORS
        lesson = get_object_or_404(Lesson, id=lesson_id)
        cards = list(lesson.cards_ordered().prefetch_related("choices"))
        cards_data = _serialize_cards(cards)
        return render(request, "education/lesson_editor.html", {
            "lesson": lesson,
            "course": lesson.course,
            "cards_json": json.dumps(cards_data, ensure_ascii=False),
            "is_new": False,
            "colors": LESSON_COLORS,
        })

    def post(self, request, lesson_id):
        from .models import Lesson
        from django.db import transaction

        lesson = get_object_or_404(Lesson, id=lesson_id)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "bad json"}, status=400)

        if "title" in data:
            lesson.title = data["title"]
        if "description" in data:
            lesson.description = data["description"]
        if "color" in data:
            lesson.color = data["color"]
        lesson.save()

        with transaction.atomic():
            _save_cards(lesson, data.get("cards", []))

        return JsonResponse({"ok": True, "redirect": f"/education/courses/{lesson.course_id}/"})


class LessonCreateEditorView(RoleRequiredMixin, View):
    """Создание нового урока через блочный редактор."""
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get(self, request, course_id):
        from .models import LESSON_COLORS
        course = get_object_or_404(Course, id=course_id)
        return render(request, "education/lesson_editor.html", {
            "lesson": None,
            "course": course,
            "cards_json": "[]",
            "is_new": True,
            "colors": LESSON_COLORS,
        })

    def post(self, request, course_id):
        from .models import Lesson
        from django.db import transaction

        course = get_object_or_404(Course, id=course_id)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "bad json"}, status=400)

        max_order = course.lessons.count() + 1
        lesson = Lesson.objects.create(
            course=course,
            title=data.get("title", "Новый урок"),
            description=data.get("description", ""),
            order=max_order,
            color=data.get("color", "violet"),
        )

        with transaction.atomic():
            _save_cards(lesson, data.get("cards", []))

        return JsonResponse({"ok": True, "redirect": f"/education/courses/{course_id}/"})


# ---------- MENTOR: подписка/отписка на курс ----------
class MentorSubscribeCourseView(RoleRequiredMixin, View):
    allowed_roles = (User.Role.MENTOR,)

    def post(self, request, course_id):
        from apps.mentors.models import Mentor
        course = get_object_or_404(Course, id=course_id)
        mentor = get_object_or_404(Mentor, user=request.user)
        course.mentors.add(mentor)
        return redirect("mentor_dashboard")


class MentorUnsubscribeCourseView(RoleRequiredMixin, View):
    allowed_roles = (User.Role.MENTOR,)

    def post(self, request, course_id):
        from apps.mentors.models import Mentor
        course = get_object_or_404(Course, id=course_id)
        mentor = get_object_or_404(Mentor, user=request.user)
        course.mentors.remove(mentor)
        return redirect("mentor_dashboard")


# ---------- Детальная страница вебинара ----------
class ScheduleDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        schedule = get_object_or_404(
            Schedule.objects.select_related("course", "mentor", "mentor__user", "course__category"),
            pk=pk
        )
        return render(request, "education/webinar_detail.html", {"schedule": schedule})


# ---------- MENTOR: Создание курса (визард с уроками) ----------
class CourseCreateWizardView(RoleRequiredMixin, View):
    """Полная страница создания курса с inline-добавлением уроков и блоков (Google Forms стиль)."""
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get(self, request):
        from .models import LESSON_COLORS, CourseCategory
        tracks = Track.objects.all()
        categories = CourseCategory.objects.all()
        return render(request, "education/course_wizard.html", {
            "tracks": tracks,
            "categories": categories,
            "colors": LESSON_COLORS,
        })

    def post(self, request):
        from .models import Lesson, CourseCategory
        from django.db import transaction

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "bad json"}, status=400)

        track_id = data.get("track_id")
        category_id = data.get("category_id")
        track = get_object_or_404(Track, id=track_id) if track_id else Track.objects.first()
        category = None
        if category_id:
            category = CourseCategory.objects.filter(id=category_id).first()

        with transaction.atomic():
            course = Course.objects.create(
                track=track,
                name=data.get("name", "Новый курс"),
                description=data.get("description", ""),
                category=category,
                format=data.get("format", "онлайн"),
                duration_hours=data.get("duration_hours", 0),
            )

            if request.user.role == User.Role.MENTOR:
                from apps.mentors.models import Mentor
                mentor = Mentor.objects.filter(user=request.user).first()
                if mentor:
                    course.mentors.add(mentor)

            lessons_data = data.get("lessons", [])
            for l_idx, lesson_data in enumerate(lessons_data):
                lesson = Lesson.objects.create(
                    course=course,
                    title=lesson_data.get("title", f"Урок {l_idx + 1}"),
                    description=lesson_data.get("description", ""),
                    order=l_idx + 1,
                    color=lesson_data.get("color", "violet"),
                )
                _save_cards(lesson, lesson_data.get("cards", []))

            course.duration_hours = len(lessons_data)
            course.save()

        return JsonResponse({"ok": True, "redirect": f"/education/courses/{course.id}/"})


# ---------- API: поиск учеников ----------
class StudentSearchAPIView(RoleRequiredMixin, View):
    """AJAX endpoint: поиск учеников по имени/фамилии для назначения на вебинар."""
    allowed_roles = (User.Role.ADMIN, User.Role.MENTOR)

    def get(self, request):
        q = request.GET.get("q", "").strip()
        if len(q) < 2:
            return JsonResponse({"results": []})
        from django.db.models import Q
        students = (
            Student.objects
            .select_related("user")
            .filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__email__icontains=q)
            )[:15]
        )
        results = [
            {
                "id": s.user_id,
                "name": s.user.get_full_name() or s.user.email,
                "email": s.user.email,
            }
            for s in students
        ]
        return JsonResponse({"results": results})
