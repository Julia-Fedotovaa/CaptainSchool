from django.db import models
from apps.users.models import User


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        verbose_name="Пользователь"
    )
    birth_date = models.DateField(verbose_name="Дата рождения")
    education_level = models.CharField(max_length=100, verbose_name="Уровень образования")
    interests = models.TextField(blank=True, verbose_name="Интересы")
    study_status = models.CharField(max_length=100, verbose_name="Статус обучения")
    initial_password = models.CharField(
        max_length=100, blank=True, default="",
        verbose_name="Начальный пароль",
        help_text="Сохраняется при создании ребёнка родителем"
    )

    class Meta:
        verbose_name = "Обучающийся"
        verbose_name_plural = "Обучающиеся"

    def __str__(self):
        return self.user.get_full_name()


class Parent(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        verbose_name="Пользователь"
    )
    relation_degree = models.CharField(max_length=50, verbose_name="Степень родства")
    students = models.ManyToManyField(
        Student, related_name="parents",
        verbose_name="Дети"
    )

    class Meta:
        verbose_name = "Родитель"
        verbose_name_plural = "Родители"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.relation_degree})"


class StudentStats(models.Model):
    """Игровая статистика ученика: тесты, время, ответы."""

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="stats",
        primary_key=True,
        verbose_name="Обучающийся"
    )
    quizzes_passed = models.PositiveIntegerField(
        default=0,
        verbose_name="Тестов пройдено"
    )
    # Лучшее время прохождения теста в секундах (None = нет данных)
    best_time_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Лучшее время (сек)"
    )
    correct_answers = models.PositiveIntegerField(
        default=0,
        verbose_name="Правильных ответов"
    )

    class Meta:
        verbose_name = "Статистика ученика"
        verbose_name_plural = "Статистика учеников"

    def __str__(self):
        return f"Статистика: {self.student}"

    @property
    def best_time_display(self) -> str:
        """Возвращает лучшее время в формате 'Xмин Yс' или '—'."""
        if self.best_time_seconds is None:
            return "—"
        minutes = self.best_time_seconds // 60
        seconds = self.best_time_seconds % 60
        if minutes:
            return f"{minutes}мин {seconds}с"
        return f"{seconds}с"


class Badge(models.Model):
    """Тип достижения (медали, звания и т.п.)."""

    MEDAL_COLORS = [
        ("comeback", "Comeback (синий/жёлтый)"),
        ("lucky", "Lucky (зелёный/фиолетовый)"),
        ("winner", "Winner (оранжевый/зелёный)"),
        ("gold", "Gold (золотой)"),
        ("silver", "Silver (серебряный)"),
        ("bronze", "Bronze (бронзовый)"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    course = models.ForeignKey(
        "education.Course",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="badges",
        verbose_name="Курс (если привязан к курсу)"
    )
    color_style = models.CharField(
        max_length=20,
        choices=MEDAL_COLORS,
        default="winner",
        verbose_name="Стиль медали"
    )
    icon = models.CharField(
        max_length=50, blank=True,
        verbose_name="Bootstrap-иконка (bi-*)",
        help_text="Например: bi-star-fill"
    )

    @property
    def display_name(self) -> str:
        """Читаемое имя значка (часть до | в description)."""
        if "|" in self.description:
            return self.description.split("|", 1)[0]
        return self.description

    @property
    def display_desc(self) -> str:
        """Описание значка (часть после | в description)."""
        if "|" in self.description:
            return self.description.split("|", 1)[1]
        return ""

    class Meta:
        verbose_name = "Тип достижения"
        verbose_name_plural = "Типы достижений"

    def __str__(self):
        return self.name

    # ---- цвета для SVG медали ----
    COLOR_MAP = {
        "comeback": ("#4a90d9", "#f5a623"),
        "lucky": ("#34c759", "#7748FF"),
        "winner": ("#ff6b35", "#34c759"),
        "gold": ("#FFD700", "#FFA500"),
        "silver": ("#C0C0C0", "#A9A9A9"),
        "bronze": ("#CD7F32", "#8B4513"),
    }

    @property
    def color_a(self):
        return self.COLOR_MAP.get(self.color_style, ("#4a90d9", "#f5a623"))[0]

    @property
    def color_b(self):
        return self.COLOR_MAP.get(self.color_style, ("#4a90d9", "#f5a623"))[1]


class StudentBadge(models.Model):
    """Связь ученик ↔ достижение (с датой получения)."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="badges",
        verbose_name="Обучающийся"
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="student_badges",
        verbose_name="Достижение"
    )
    awarded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата получения"
    )

    class Meta:
        verbose_name = "Достижение ученика"
        verbose_name_plural = "Достижения учеников"
        unique_together = ("student", "badge")

    def __str__(self):
        return f"{self.student} — {self.badge}"
