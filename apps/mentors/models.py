from django.db import models
from apps.users.models import User

class Mentor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True,
        verbose_name="Пользователь"
    )
    specialization = models.CharField(max_length=200, verbose_name="Специализация")
    experience_years = models.PositiveIntegerField(verbose_name="Опыт работы (лет)")
    bio = models.TextField(verbose_name="Описание профиля")

    class Meta:
        verbose_name = "Наставник"
        verbose_name_plural = "Наставники"
