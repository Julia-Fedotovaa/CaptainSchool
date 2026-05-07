# ================================================================
# apps/students/badges.py  — НОВЫЙ ФАЙЛ
#
# Движок достижений. Вызывай check_and_award(student, course)
# после каждого завершения урока.
# ================================================================

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.students.models import Student
    from apps.education.models import Course


# ── Коды всех достижений ─────────────────────────────────────────
# Уровневые (прогресс курса)
BADGE_FIRST_LESSON       = "first_lesson"        # бронза — первый урок завершён
BADGE_HALF_COURSE        = "half_course"          # серебро — 50% курса
BADGE_FULL_COURSE        = "full_course"          # золото  — 100% курса

# Уровневые (идеальные уроки — score 100%)
BADGE_PERFECT_FIRST      = "perfect_first"        # comeback — 1 урок идеально
BADGE_PERFECT_HALF       = "perfect_half"         # lucky    — 50% уроков идеально
BADGE_PERFECT_ALL        = "perfect_all"          # winner   — все уроки идеально

# Одиночные достижения
BADGE_SPEED_DEMON        = "speed_demon"          # comeback — урок < 3 минут
BADGE_NIGHT_OWL          = "night_owl"            # lucky    — занятие после 22:00
BADGE_EARLY_BIRD         = "early_bird"           # comeback — занятие до 07:00
BADGE_STREAK_3           = "streak_3"             # silver   — 3 урока подряд за 3 дня
BADGE_COMEBACK           = "comeback"             # comeback — пересдал урок и улучшил оценку
BADGE_EXPLORER           = "explorer"             # lucky    — записался на 3 разные категории
BADGE_PERFECTIONIST      = "perfectionist"        # gold     — 10 идеальных уроков суммарно
BADGE_DEDICATED          = "dedicated"            # silver   — завершил 5 курсов

# Спецификации значков: (код, название, описание, color_style, icon)
BADGE_SPECS: list[tuple] = [
    # Прогресс курса
    (BADGE_FIRST_LESSON,  "Первый шаг",        "Завершил первый урок в курсе",                       "bronze",  "bi-play-circle-fill"),
    (BADGE_HALF_COURSE,   "Полпути",            "Прошёл 50% курса",                                   "silver",  "bi-lightning-fill"),
    (BADGE_FULL_COURSE,   "Мастер курса",       "Прошёл курс полностью",                              "gold",    "bi-trophy-fill"),
    # Идеальные уроки
    (BADGE_PERFECT_FIRST, "Отличник",           "Прошёл урок с результатом 100%",                     "comeback","bi-star-fill"),
    (BADGE_PERFECT_HALF,  "Полупрофи",          "50% уроков в курсе пройдены на 100%",                "lucky",   "bi-patch-check-fill"),
    (BADGE_PERFECT_ALL,   "Легенда",            "Все уроки курса пройдены идеально",                  "winner",  "bi-award-fill"),
    # Одиночные
    (BADGE_SPEED_DEMON,   "Скоростной",         "Прошёл урок менее чем за 3 минуты",                  "comeback","bi-rocket-takeoff-fill"),
    (BADGE_NIGHT_OWL,     "Ночная сова",        "Занимался после 22:00",                              "lucky",   "bi-moon-stars-fill"),
    (BADGE_EARLY_BIRD,    "Ранняя пташка",      "Занимался до 7 утра",                                "comeback","bi-sunrise-fill"),
    (BADGE_STREAK_3,      "На волне",           "3 урока за 3 дня подряд",                            "silver",  "bi-fire"),
    (BADGE_COMEBACK,      "Comeback",           "Пересдал урок и улучшил оценку",                     "comeback","bi-arrow-counterclockwise"),
    (BADGE_EXPLORER,      "Исследователь",      "Записался на курсы 3 разных категорий",              "lucky",   "bi-compass-fill"),
    (BADGE_PERFECTIONIST, "Перфекционист",      "10 уроков с оценкой 100% суммарно",                  "gold",    "bi-gem"),
    (BADGE_DEDICATED,     "Преданный",          "Завершил 5 курсов полностью",                        "gold",    "bi-heart-fill"),
]


def ensure_badges_exist() -> None:
    """Создаёт все Badge-объекты в БД если их ещё нет. Вызывай из seed или AppConfig.ready()."""
    from apps.students.models import Badge
    for code, name, desc, color, icon in BADGE_SPECS:
        Badge.objects.get_or_create(
            name=code,                          # code — уникальный идентификатор
            defaults={
                "description":  f"{name}|{desc}",  # "Первый шаг|Завершил первый урок..."
                "color_style":  color,
                "icon":         icon,
            }
        )
        # Обновляем поля если значок уже есть
        Badge.objects.filter(name=code).update(
            description=f"{name}|{desc}", color_style=color, icon=icon
        )


def _award(student: "Student", badge_code: str) -> bool:
    """Выдаёт значок студенту. Возвращает True если выдан впервые."""
    from apps.students.models import Badge, StudentBadge
    try:
        badge = Badge.objects.get(name=badge_code)
    except Badge.DoesNotExist:
        return False
    _, created = StudentBadge.objects.get_or_create(student=student, badge=badge)
    return created


def check_and_award(student: "Student", course: "Course", lesson_progress=None) -> list[str]:
    """
    Главная точка входа. Проверяет все условия и выдаёт заработанные значки.
    lesson_progress — только что завершённый LessonProgress (опционально).
    Возвращает список кодов НОВЫХ значков.
    """
    from apps.education.models import LessonProgress, Enrollment
    from apps.progress.models import Progress
    from apps.students.models import StudentStats
    from django.utils import timezone

    awarded = []

    lessons      = list(course.lessons.all())
    total        = len(lessons)
    if not total:
        return awarded

    completed_lps = LessonProgress.objects.filter(
        student=student, lesson__in=lessons, status="completed"
    )
    completed_count   = completed_lps.count()
    perfect_count     = sum(1 for lp in completed_lps if lp.score_percent == 100)

    # ── 1. Прогресс курса ──────────────────────────────────────────
    if completed_count >= 1:
        if _award(student, BADGE_FIRST_LESSON):
            awarded.append(BADGE_FIRST_LESSON)

    if completed_count >= total // 2 and total >= 2:
        if _award(student, BADGE_HALF_COURSE):
            awarded.append(BADGE_HALF_COURSE)

    if completed_count >= total:
        if _award(student, BADGE_FULL_COURSE):
            awarded.append(BADGE_FULL_COURSE)

    # ── 2. Идеальные уроки ────────────────────────────────────────
    if perfect_count >= 1:
        if _award(student, BADGE_PERFECT_FIRST):
            awarded.append(BADGE_PERFECT_FIRST)

    if perfect_count >= total // 2 and total >= 2:
        if _award(student, BADGE_PERFECT_HALF):
            awarded.append(BADGE_PERFECT_HALF)

    if perfect_count >= total and total >= 1:
        if _award(student, BADGE_PERFECT_ALL):
            awarded.append(BADGE_PERFECT_ALL)

    # ── 3. Специальные: только если есть lesson_progress ──────────
    if lesson_progress is not None:
        lp = lesson_progress

        # Скоростной: урок < 3 минут
        if lp.completed_at and lp.started_at:
            secs = (lp.completed_at - lp.started_at).total_seconds()
            if secs < 180:
                if _award(student, BADGE_SPEED_DEMON):
                    awarded.append(BADGE_SPEED_DEMON)

        # Ночная сова: после 22:00 (по времени завершения)
        if lp.completed_at:
            local_hour = lp.completed_at.astimezone().hour
            if local_hour >= 22:
                if _award(student, BADGE_NIGHT_OWL):
                    awarded.append(BADGE_NIGHT_OWL)
            # Ранняя пташка: до 07:00
            if local_hour < 7:
                if _award(student, BADGE_EARLY_BIRD):
                    awarded.append(BADGE_EARLY_BIRD)

        # Comeback: предыдущий результат хуже текущего
        # Смотрим — если score сейчас 100%, а был < 100%
        if lp.score_percent == 100 and lp.completed_at:
            # Проверяем историю через StudentStats (предыдущие попытки не хранятся отдельно,
            # но если значок "comeback" ещё не выдан — считаем что улучшил)
            # Простое правило: выдаём если урок был completed более одного раза
            # (т.е. was_reset значит пересдавал)
            from apps.students.models import StudentBadge, Badge as B
            if not StudentBadge.objects.filter(student=student, badge__name=BADGE_COMEBACK).exists():
                # Если total_test_cards > 0 и это не первое прохождение
                # (определяем косвенно: если correct_answers == total_test_cards после пересдачи)
                # Упрощённо: выдаём при идеальном результате если урок пересдавался
                pass  # осторожно — этот значок лучше выдавать явно (см. ниже)

    # ── 4. Streak: 3 урока за 3 разных дня подряд ─────────────────
    all_completions = (
        LessonProgress.objects
        .filter(student=student, status="completed")
        .exclude(completed_at=None)
        .order_by("-completed_at")
        .values_list("completed_at", flat=True)[:10]
    )
    dates = sorted(set(dt.date() for dt in all_completions), reverse=True)
    if len(dates) >= 3:
        from datetime import timedelta
        streak = 1
        for i in range(1, len(dates)):
            if (dates[i-1] - dates[i]).days == 1:
                streak += 1
                if streak >= 3:
                    if _award(student, BADGE_STREAK_3):
                        awarded.append(BADGE_STREAK_3)
                    break
            else:
                break

    # ── 5. Исследователь: 3 разные категории ──────────────────────
    enrolled_cats = (
        Enrollment.objects
        .filter(student=student)
        .select_related("course__category")
        .values_list("course__category__id", flat=True)
        .distinct()
    )
    if len(set(enrolled_cats)) >= 3:
        if _award(student, BADGE_EXPLORER):
            awarded.append(BADGE_EXPLORER)

    # ── 6. Перфекционист: 10 идеальных уроков суммарно ────────────
    total_perfect = LessonProgress.objects.filter(
        student=student, status="completed"
    ).count()  # считаем через score_percent ниже
    # (нет aggregate, считаем через Python)
    all_lps = LessonProgress.objects.filter(student=student, status="completed")
    real_perfect = sum(1 for lp in all_lps if lp.score_percent == 100)
    if real_perfect >= 10:
        if _award(student, BADGE_PERFECTIONIST):
            awarded.append(BADGE_PERFECTIONIST)

    # ── 7. Преданный: 5 завершённых курсов ────────────────────────
    from apps.progress.models import Progress as Prog
    finished_courses = Prog.objects.filter(
        student=student, completion_percent=100
    ).count()
    if finished_courses >= 5:
        if _award(student, BADGE_DEDICATED):
            awarded.append(BADGE_DEDICATED)

    return awarded


def _award_course_badge(student: "Student", course: "Course", badge_code: str, display_name: str, display_desc: str, color: str, icon: str) -> bool:
    """Выдаёт курсо-специфичный значок. Создаёт Badge если не существует."""
    from apps.students.models import Badge, StudentBadge
    code = f"{badge_code}_{course.id}"
    badge, _ = Badge.objects.get_or_create(
        name=code,
        course=course,
        defaults={
            "description": f"{display_name}: {course.name}|{display_desc}",
            "color_style": color,
            "icon": icon,
        }
    )
    _, created = StudentBadge.objects.get_or_create(student=student, badge=badge)
    return created


def check_course_achievements(student: "Student", course: "Course") -> list[str]:
    """Проверяет и выдаёт курсо-специфичные ранжированные достижения."""
    from apps.education.models import LessonProgress
    from apps.progress.models import Progress

    awarded = []
    lessons = list(course.lessons.all())
    total = len(lessons)
    if not total:
        return awarded

    completed_lps = LessonProgress.objects.filter(
        student=student, lesson__in=lessons, status="completed"
    )
    completed_count = completed_lps.count()
    perfect_count = sum(1 for lp in completed_lps if lp.score_percent == 100)
    pct = round(completed_count / total * 100) if total else 0

    # Прогресс курса: бронза 25%, серебро 50%, золото 100%
    if pct >= 25:
        code = f"course_progress_bronze_{course.id}"
        if _award_course_badge(student, course, "course_progress_bronze",
                               "Новичок", f"Пройдено 25% курса «{course.name}»", "bronze", "bi-bookmark-fill"):
            awarded.append(code)
    if pct >= 50:
        code = f"course_progress_silver_{course.id}"
        if _award_course_badge(student, course, "course_progress_silver",
                               "Практик", f"Пройдено 50% курса «{course.name}»", "silver", "bi-bookmark-star-fill"):
            awarded.append(code)
    if pct >= 100:
        code = f"course_progress_gold_{course.id}"
        if _award_course_badge(student, course, "course_progress_gold",
                               "Мастер", f"Пройден полностью курс «{course.name}»", "gold", "bi-trophy-fill"):
            awarded.append(code)

    # Перфекционист курса: все уроки на 100%
    if perfect_count >= total and total >= 1:
        code = f"course_perfectionist_{course.id}"
        if _award_course_badge(student, course, "course_perfectionist",
                               "Перфекционист", f"Все уроки курса «{course.name}» на 100%", "winner", "bi-gem"):
            awarded.append(code)

    return awarded


def award_comeback(student: "Student", lesson_progress, prev_score: int) -> bool:
    """
    Вызывай явно когда пересдача улучшила оценку.
    prev_score — предыдущий score_percent (до сброса).
    """
    if lesson_progress.score_percent > prev_score:
        return _award(student, BADGE_COMEBACK)
    return False