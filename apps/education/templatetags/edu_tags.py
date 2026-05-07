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
