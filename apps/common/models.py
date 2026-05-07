from django.db import models


class ContactMessage(models.Model):
    name       = models.CharField(max_length=150, verbose_name="Имя")
    email      = models.EmailField(verbose_name="Email")
    message    = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    is_read    = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name        = "Обращение"
        verbose_name_plural = "Обращения"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.created_at:%d.%m.%Y %H:%M}"
