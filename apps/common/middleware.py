from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.exceptions import TemplateDoesNotExist


# Статусы, для которых кастомная страница показывается всегда (и в DEBUG, и в production)
_ALWAYS = {400, 403, 404}

# Статусы, для которых кастомная страница показывается только в production (DEBUG=False),
# чтобы не скрывать стектрейс во время разработки
_PROD_ONLY = {500}


class CustomErrorMiddleware:
    """
    Перехватывает ответы с кодами 400/403/404/500 и подменяет их
    кастомными HTML-шаблонами (400.html, 403.html, 404.html, 500.html).

    400/403/404 — показываются всегда (в т.ч. при DEBUG=True).
    500        — только при DEBUG=False, чтобы не скрывать стектрейс.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        status = response.status_code

        show_custom = status in _ALWAYS or (
            status in _PROD_ONLY and not settings.DEBUG
        )

        if show_custom:
            try:
                content = render_to_string(f"{status}.html", request=request)
                return HttpResponse(content, status=status)
            except TemplateDoesNotExist:
                pass  # нет шаблона — отдаём оригинальный ответ

        return response
