from django import template

register = template.Library()


@register.filter
def pluralize_lessons(count):
    """Правильное склонение слова 'урок' по числу: 1 урок, 2 урока, 5 уроков."""
    try:
        count = int(count)
    except (ValueError, TypeError):
        return "уроков"
    if 11 <= count % 100 <= 19:
        return "уроков"
    last = count % 10
    if last == 1:
        return "урок"
    if 2 <= last <= 4:
        return "урока"
    return "уроков"


@register.filter
def pluralize_students(count):
    """Правильное склонение слова 'ученик' по числу: 1 ученик, 2 ученика, 5 учеников."""
    try:
        count = int(count)
    except (ValueError, TypeError):
        return "Учеников"
    if 11 <= count % 100 <= 19:
        return "Учеников"
    last = count % 10
    if last == 1:
        return "Ученик"
    if 2 <= last <= 4:
        return "Ученика"
    return "Учеников"


@register.filter
def pluralize_webinars(count):
    """Правильное склонение слова 'вебинар' по числу: 1 вебинар, 2 вебинара, 5 вебинаров."""
    try:
        count = int(count)
    except (ValueError, TypeError):
        return "Вебинаров"
    if 11 <= count % 100 <= 19:
        return "Вебинаров"
    last = count % 10
    if last == 1:
        return "Вебинар"
    if 2 <= last <= 4:
        return "Вебинара"
    return "Вебинаров"
