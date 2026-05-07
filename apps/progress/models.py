from django.db import models
from apps.students.models import Student
from apps.education.models import Course


class Progress(models.Model):
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
    completion_percent = models.PositiveIntegerField(
        verbose_name="Процент прохождения"
    )
    result = models.CharField(
        max_length=100,
        verbose_name="Результат"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Прогресс обучения"
        verbose_name_plural = "Прогресс обучения"
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} — {self.course} ({self.completion_percent}%)"
