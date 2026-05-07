# EduPlatform

Онлайн-платформа для обучения школьников с персональными траекториями, системой менторства и геймификацией.

## Технологии

- **Backend:** Django 6.0, Django REST Framework 3.17, SimpleJWT
- **Frontend:** Django Templates (Jinja2-совместимые), Bootstrap Icons, Poppins (Google Fonts)
- **БД:** SQLite (dev) — легко меняется на PostgreSQL через `DATABASES` в settings
- **Медиа:** Pillow для обработки изображений

## Роли пользователей

| Роль | Возможности |
|------|-------------|
| **Ученик** | Проходит вступительный тест, получает персональную траекторию, проходит уроки, получает достижения |
| **Родитель** | Следит за прогрессом детей, записывает их на курсы, видит статистику |
| **Ментор** | Создаёт и ведёт курсы, проверяет развёрнутые ответы учеников |
| **Администратор** | Полный доступ через Django Admin |

## Структура приложений

```
apps/
├── users/          # Кастомная модель User, авторизация, дашборды, страница всех курсов
├── students/       # Модели Student, Parent, StudentStats, Badge, достижения
├── mentors/        # Модель Mentor, привязка к курсам
├── education/      # Course, Lesson, LessonCard, Enrollment, LessonProgress,
│                   # PlacementTest, OpenAnswerSubmission, Schedule, CourseReview
├── trajectories/   # IndividualTrajectory — персональный план обучения
├── progress/       # Progress — агрегированный прогресс по курсу
└── common/         # Миксины, middleware, ContactMessage, формы
```

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd EduPlatform

# 2. Создать и активировать виртуальное окружение
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Установить зависимости
pip install django==6.0.3 djangorestframework==3.17.1 \
            djangorestframework-simplejwt==5.5.1 pillow==12.1.1

# 4. Применить миграции
python manage.py migrate

# 5. (Опционально) Заполнить тестовыми данными
python run_seed.py
python seed_placement_test.py

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver
```

Платформа доступна по адресу: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Админка: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Основные URL

| Путь | Описание |
|------|----------|
| `/` | Главная страница |
| `/courses/` | Все курсы |
| `/education/courses/<id>/` | Страница курса |
| `/education/lessons/<id>/play/` | Плеер урока |
| `/education/lessons/<id>/result/` | Результат урока |
| `/education/placement-test/` | Вступительный тест |
| `/users/dashboard/` | Личный кабинет (редирект по роли) |
| `/students/parent/children/` | Список детей родителя |
| `/admin/` | Django Admin |

## Ключевые особенности

### Плеер урока
Уроки состоят из карточек четырёх типов:
- **info** — информационный блок
- **test** — тест с одним правильным вариантом (автопроверка)
- **matching** — сопоставление пар (автопроверка)
- **open_answer** — развёрнутый ответ (проверяется ментором)

### Оценивание
Оценка выставляется по всем карточкам с проверкой:
- Тест + сопоставление → считаются сразу
- Развёрнутые ответы → учитываются после проверки ментором
- Итоговый балл: `(верные тест + одобренные открытые) / (всего тест + все открытые) × 100%`

| Балл | Оценка |
|------|--------|
| ≥ 90% | A |
| ≥ 75% | B |
| ≥ 60% | C |
| ≥ 40% | D |
| < 40% | F |

### Персональная траектория
После вступительного теста система определяет склонности ученика по категориям и автоматически формирует список курсов.

### Геймификация
- Достижения (badges) за прохождение уроков, курсов, серии побед
- Статистика: уроков завершено, рекорд времени за урок, верных ответов всего
- Прогресс-бар по каждому курсу

## Переменные окружения (опционально)

Для production рекомендуется вынести в `.env`:

```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@host/db
```
