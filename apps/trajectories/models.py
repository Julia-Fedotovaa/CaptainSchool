from django.db import models
from apps.students.models import Student
from apps.education.models import Track, Course


class IndividualTrajectory(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="trajectories",
        verbose_name="Обучающийся"
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        verbose_name="Образовательный трек"
    )
    category = models.ForeignKey(
        "education.CourseCategory",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Категория"
    )
    start_date = models.DateField(
        verbose_name="Дата начала"
    )
    status = models.CharField(
        max_length=100,
        verbose_name="Статус траектории"
    )
    goals = models.TextField(
        verbose_name="Цели обучения"
    )

    class Meta:
        verbose_name = "Индивидуальная траектория"
        verbose_name_plural = "Индивидуальные траектории"
        unique_together = ("student", "track")

    def __str__(self):
        return f"{self.student} — {self.track}"

    def ordered_courses(self):
        return self.trajectory_courses.select_related("course").order_by("order")


class TrajectoryCourse(models.Model):
    trajectory = models.ForeignKey(
        IndividualTrajectory,
        on_delete=models.CASCADE,
        related_name="trajectory_courses",
        verbose_name="Траектория"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Курс в траектории"
        verbose_name_plural = "Курсы в траектории"
        ordering = ["order"]
        unique_together = ("trajectory", "course")

    def __str__(self):
        return f"{self.trajectory} — #{self.order} {self.course}"
