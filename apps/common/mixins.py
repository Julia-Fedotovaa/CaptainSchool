from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if not self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        if not hasattr(request.user, "role"):
            return redirect("login")
            # raise PermissionDenied("У пользователя нет роли.")

        if request.user.role not in self.allowed_roles:
            return redirect("login")
            # raise PermissionDenied("Недостаточно прав.")
        return super().dispatch(request, *args, **kwargs)


class FormTitleMixin:
    form_title_create: str = "Создание"
    form_title_update: str = "Редактирование"

    def get_form_title(self) -> str:
        # если есть object -> update, иначе create
        if getattr(self, "object", None) is not None:
            return self.form_title_update
        return self.form_title_create

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = self.get_form_title()
        context["form_subtitle"] = "Заполните поля ниже и сохраните изменения"
        return context
