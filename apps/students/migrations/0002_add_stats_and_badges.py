# apps/students/migrations/XXXX_add_stats_and_badges.py
# Переименуй файл согласно следующему номеру миграции в твоём проекте,
# например: 0002_add_stats_and_badges.py

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    # Замени '0001_initial' на реальное имя предыдущей миграции students
    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        # ---- Badge ----
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('color_style', models.CharField(
                    choices=[
                        ('comeback', 'Comeback (синий/жёлтый)'),
                        ('lucky',    'Lucky (зелёный/фиолетовый)'),
                        ('winner',   'Winner (оранжевый/зелёный)'),
                        ('gold',     'Gold (золотой)'),
                        ('silver',   'Silver (серебряный)'),
                        ('bronze',   'Bronze (бронзовый)'),
                    ],
                    default='winner', max_length=20, verbose_name='Стиль медали'
                )),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='Bootstrap-иконка (bi-*)')),
            ],
            options={'verbose_name': 'Тип достижения', 'verbose_name_plural': 'Типы достижений'},
        ),

        # ---- StudentStats ----
        migrations.CreateModel(
            name='StudentStats',
            fields=[
                ('student', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True, serialize=False,
                    related_name='stats',
                    to='students.student',
                    verbose_name='Обучающийся'
                )),
                ('quizzes_passed',   models.PositiveIntegerField(default=0, verbose_name='Тестов пройдено')),
                ('best_time_seconds', models.PositiveIntegerField(blank=True, null=True, verbose_name='Лучшее время (сек)')),
                ('correct_answers',  models.PositiveIntegerField(default=0, verbose_name='Правильных ответов')),
            ],
            options={'verbose_name': 'Статистика ученика', 'verbose_name_plural': 'Статистика учеников'},
        ),

        # ---- StudentBadge ----
        migrations.CreateModel(
            name='StudentBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='badges',
                    to='students.student',
                    verbose_name='Обучающийся'
                )),
                ('badge', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='student_badges',
                    to='students.badge',
                    verbose_name='Достижение'
                )),
                ('awarded_at', models.DateTimeField(
                    default=django.utils.timezone.now,
                    verbose_name='Дата получения'
                )),
            ],
            options={
                'verbose_name': 'Достижение ученика',
                'verbose_name_plural': 'Достижения учеников',
                'unique_together': {('student', 'badge')},
            },
        ),
    ]