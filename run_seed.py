
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduPlatform.settings')
django.setup()
# ================================================================
# seed_badges.py — python manage.py shell < seed_badges.py
# Создаёт все Badge-записи в БД
# ================================================================
from apps.students.badges import ensure_badges_exist, BADGE_SPECS
from apps.students.models import Badge

ensure_badges_exist()

print(f"✅ Создано / обновлено {Badge.objects.count()} достижений:")
for code, name, desc, color, _ in BADGE_SPECS:
    b = Badge.objects.get(name=code)
    print(f"  [{b.color_style:8}] {code:22} — {desc}")