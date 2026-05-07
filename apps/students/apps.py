from django.apps import AppConfig


class StudentsConfig(AppConfig):
    name = 'apps.students'
    verbose_name = "Ученики и Родители"

    def ready(self):
        import apps.students.signals
        # Создание бейджей откладываем на post_migrate
        from django.db.models.signals import post_migrate
        post_migrate.connect(self._ensure_badges, sender=self)

    @staticmethod
    def _ensure_badges(sender, **kwargs):
        try:
            from apps.students.badges import ensure_badges_exist
            ensure_badges_exist()
        except Exception:
            pass
