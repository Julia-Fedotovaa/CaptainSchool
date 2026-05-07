from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = "student", "Обучающийся"
        PARENT = "parent", "Родитель"
        MENTOR = "mentor", "Наставник"
        ADMIN = "admin", "Администратор"

    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Никнейм"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        verbose_name="Роль",
        null=True,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ в админку")

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата регистрации"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    objects = UserManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username + f" ({self.get_full_name()})"
