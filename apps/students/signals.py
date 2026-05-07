from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User


@receiver(post_save, sender=User)
def create_role_profile(sender, instance, created, **kwargs):
    """Автоматически создаёт профиль Student/Parent/Mentor при создании пользователя."""
    if not created:
        return

    if instance.role == User.Role.STUDENT:
        from .models import Student
        Student.objects.get_or_create(
            user=instance,
            defaults={
                "birth_date": date(2000, 1, 1),
                "education_level": "Не указан",
                "study_status": "Активен",
            }
        )
    elif instance.role == User.Role.PARENT:
        from .models import Parent
        Parent.objects.get_or_create(
            user=instance,
            defaults={"relation_degree": "Родитель"}
        )
    elif instance.role == User.Role.MENTOR:
        from apps.mentors.models import Mentor
        Mentor.objects.get_or_create(
            user=instance,
            defaults={
                "specialization": "Не указана",
                "experience_years": 0,
                "bio": "",
            }
        )
