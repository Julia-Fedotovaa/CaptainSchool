from django.db import models
from django.db.models import Avg

from apps.students.models import Student


class Track(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    format = models.CharField(max_length=50, verbose_name="Формат")
    difficulty = models.CharField(max_length=50, verbose_name="Уровень сложности")

    class Meta:
        verbose_name = "Образовательный трек"
        verbose_name_plural = "Образовательные треки"

    def __str__(self):
        return self.name


class Course(models.Model):
    track = models.ForeignKey(
        Track, on_delete=models.CASCADE, related_name="courses",
        verbose_name="Трек"
    )
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    category = models.ForeignKey(
        "CourseCategory", on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Категория"
    )

    # Optional image to represent the course on the landing page
    image = models.ImageField(
        upload_to="static/courses/images/",
        null=True,
        blank=True,
        verbose_name="Изображение курса",
        help_text="Изображение, отображаемое на главной странице."
    )
    mentors = models.ManyToManyField(
        "mentors.Mentor", blank=True, related_name="courses",
        verbose_name="Наставники"
    )
    format = models.CharField(max_length=50, verbose_name="Формат")
    duration_hours = models.PositiveIntegerField(verbose_name="Кол-во уроков")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name

    @property
    def average_rating(self) -> float:
        """Return the average rating of all reviews for this course.

        If there are no reviews, return 0.0.
        """
        agg = self.reviews.aggregate(avg_rating=Avg("rating"))
        return round(agg["avg_rating"] or 0.0, 1)

    @property
    def reviews_count(self) -> int:
        """Return the total number of reviews for this course."""
        return self.reviews.count()


class CourseCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория курса"
        verbose_name_plural = "Категории курсов"

    def __str__(self):
        return self.name


class CourseReview(models.Model):
    """A review left by a student for a course.

    Stores a rating (1–5 stars) and an optional comment. Reviews are used to
    calculate the most popular courses on the homepage.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Курс",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Обучающийся",
    )
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name="Оценка",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Отзыв к курсу"
        unique_together = ('course', 'student')
        verbose_name_plural = "Отзывы к курсам"

    def __str__(self):
        return f"{self.course} — {self.rating}★"


class Schedule(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE,
        verbose_name="Курс"
    )
    mentor = models.ForeignKey(
        "mentors.Mentor", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="schedules",
        verbose_name="Наставник"
    )
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    lesson_format = models.CharField(max_length=50, verbose_name="Формат занятия")
    location = models.CharField(max_length=255, verbose_name="Место / ссылка")
    description = models.TextField(blank=True, verbose_name="Описание")
    students = models.ManyToManyField(
        Student, blank=True, related_name="schedules",
        verbose_name="Ученики"
    )

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"

    def __str__(self):
        return f"{self.course} | {self.date} {self.start_time}-{self.end_time}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Обучающийся"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс"
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата записи"
    )

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} → {self.course}"


class PlacementTest(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название теста")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Тест на определение способностей"
        verbose_name_plural = "Тесты на определение способностей"

    def __str__(self):
        return self.title

    def questions_ordered(self):
        return self.questions.order_by("order")


class PlacementQuestion(models.Model):
    TYPE_CHOICE = "choice"
    TYPE_MATCHING = "matching"
    QUESTION_TYPES = [
        (TYPE_CHOICE, "Выбор из вариантов"),
        (TYPE_MATCHING, "Соотнесение"),
    ]

    test = models.ForeignKey(PlacementTest, on_delete=models.CASCADE, related_name="questions", verbose_name="Тест")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=TYPE_CHOICE,
                                     verbose_name="Тип вопроса")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    text = models.TextField(verbose_name="Текст вопроса")
    image = models.ImageField(upload_to="placement_test/images/", null=True, blank=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Вопрос теста"
        verbose_name_plural = "Вопросы теста"
        ordering = ["order"]

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:60]}"


class ChoiceOption(models.Model):
    """Вариант ответа. category — ссылка на CourseCategory,
    означает: «если выбрал этот вариант, +1 балл к этой категории»."""
    question = models.ForeignKey(PlacementQuestion, on_delete=models.CASCADE, related_name="choices",
                                 verbose_name="Вопрос")
    text = models.CharField(max_length=500, verbose_name="Вариант ответа")
    category = models.ForeignKey(
        "CourseCategory",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="choice_options",
        verbose_name="Категория склонности",
        help_text="Какую категорию усиливает этот вариант ответа"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответа"
        ordering = ["order"]

    def __str__(self):
        return self.text


class MatchingPair(models.Model):
    """Пара для вопроса типа matching.
    category — категория, к которой относится эта пара (начисляется балл если правильно)."""
    question = models.ForeignKey(PlacementQuestion, on_delete=models.CASCADE, related_name="pairs",
                                 verbose_name="Вопрос")
    left_text = models.CharField(max_length=300, verbose_name="Левый элемент")
    right_text = models.CharField(max_length=300, verbose_name="Правый элемент")
    category = models.ForeignKey(
        "CourseCategory",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matching_pairs",
        verbose_name="Категория склонности"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Пара соотнесения"
        verbose_name_plural = "Пары соотнесения"
        ordering = ["order"]

    def __str__(self):
        return f"{self.left_text} ↔ {self.right_text}"


class PlacementTestSession(models.Model):
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUSES = [
        (STATUS_IN_PROGRESS, "В процессе"),
        (STATUS_COMPLETED, "Завершён"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="placement_sessions",
                                verbose_name="Студент")
    test = models.ForeignKey(PlacementTest, on_delete=models.CASCADE, related_name="sessions", verbose_name="Тест")
    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_IN_PROGRESS, verbose_name="Статус")
    current_question_index = models.PositiveIntegerField(default=0, verbose_name="Текущий вопрос")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Начат")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершён")

    # JSON: { category_id: score, ... }  — накапливается по мере ответов
    category_scores = models.JSONField(default=dict, verbose_name="Баллы по категориям")

    class Meta:
        verbose_name = "Сессия теста"
        verbose_name_plural = "Сессии тестов"

    def __str__(self):
        return f"{self.student} — {self.test} ({self.get_status_display()})"

    def top_categories(self, n=2):
        """Возвращает список (category, score) отсортированный по убыванию."""
        result = []
        for cat_id, score in self.category_scores.items():
            try:
                cat = CourseCategory.objects.get(pk=int(cat_id))
                result.append((cat, score))
            except CourseCategory.DoesNotExist:
                pass
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]


class PlacementAnswer(models.Model):
    session = models.ForeignKey(PlacementTestSession, on_delete=models.CASCADE, related_name="answers",
                                verbose_name="Сессия")
    question = models.ForeignKey(PlacementQuestion, on_delete=models.CASCADE, verbose_name="Вопрос")
    selected_choice = models.ForeignKey(ChoiceOption, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name="Выбранный вариант")
    # matching: { str(pair_id): right_text, ... }
    matching_answer = models.JSONField(null=True, blank=True, verbose_name="Ответ на соотнесение")

    class Meta:
        verbose_name = "Ответ на тест"
        verbose_name_plural = "Ответы на тест"
        unique_together = ("session", "question")


LESSON_COLORS = [
    ("violet", "#7748FF"),
    ("blue", "#3B82F6"),
    ("green", "#22C55E"),
    ("orange", "#F97316"),
    ("pink", "#EC4899"),
    ("teal", "#14B8A6"),
    ("red", "#EF4444"),
    ("yellow", "#EAB308"),
]


class Lesson(models.Model):
    TYPE_THEORY_TEST = "theory_test"
    TYPE_TEST_ONLY = "test_only"
    LESSON_TYPES = [
        (TYPE_THEORY_TEST, "Теория + Тест"),
        (TYPE_TEST_ONLY, "Только тест"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Название урока")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=1, verbose_name="Порядок")
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default=TYPE_THEORY_TEST,
                                   verbose_name="Тип урока")
    color = models.CharField(max_length=20, choices=LESSON_COLORS, default="violet", verbose_name="Цвет")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.name} / {self.order}. {self.title}"

    @property
    def color_hex(self):
        return dict(LESSON_COLORS).get(self.color, "#7748FF")

    def cards_ordered(self):
        return self.cards.order_by("order")

    @property
    def total_cards(self):
        return self.cards.count()


class LessonCard(models.Model):
    TYPE_THEORY = "theory"
    TYPE_TEST = "test"
    TYPE_MATCHING = "matching"
    TYPE_OPEN = "open_answer"
    CARD_TYPES = [
        (TYPE_THEORY, "Теория"),
        (TYPE_TEST, "Тест"),
        (TYPE_MATCHING, "Соотнесение"),
        (TYPE_OPEN, "Развёрнутый ответ"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="cards", verbose_name="Урок")
    card_type = models.CharField(max_length=15, choices=CARD_TYPES, default=TYPE_THEORY, verbose_name="Тип")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    content = models.TextField(blank=True, verbose_name="Текст / вопрос")
    image = models.ImageField(upload_to="lessons/cards/", null=True, blank=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Карточка урока"
        verbose_name_plural = "Карточки урока"
        ordering = ["order"]

    def __str__(self):
        return f"[{self.get_card_type_display()}] {self.lesson.title} #{self.order}"


class CardChoice(models.Model):
    card = models.ForeignKey(LessonCard, on_delete=models.CASCADE, related_name="choices", verbose_name="Карточка")
    text = models.CharField(max_length=500, verbose_name="Текст варианта")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный")
    match_text = models.CharField(max_length=500, blank=True, verbose_name="Текст для соотнесения")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответа"
        ordering = ["order"]

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text}"


class LessonProgress(models.Model):
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUSES = [
        (STATUS_NOT_STARTED, "Не начат"),
        (STATUS_IN_PROGRESS, "В процессе"),
        (STATUS_COMPLETED, "Завершён"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="lesson_progress",
                                verbose_name="Студент")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="student_progress", verbose_name="Урок")
    status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_NOT_STARTED)
    current_card_index = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    total_test_cards = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Прогресс по уроку"
        verbose_name_plural = "Прогресс по урокам"
        unique_together = ("student", "lesson")

    def __str__(self):
        return f"{self.student} / {self.lesson} — {self.get_status_display()}"

    @property
    def score_percent(self):
        if not self.total_test_cards:
            return 100
        return round(self.correct_answers / self.total_test_cards * 100)

    @property
    def grade(self):
        p = self.score_percent
        if p >= 90: return ("A", "#22C55E")
        if p >= 75: return ("B", "#3B82F6")
        if p >= 60: return ("C", "#EAB308")
        if p >= 40: return ("D", "#F97316")
        return ("F", "#EF4444")

    @property
    def completion_percent(self):
        total = self.lesson.total_cards
        if not total:
            return 0
        return round(min(self.current_card_index, total) / total * 100)
