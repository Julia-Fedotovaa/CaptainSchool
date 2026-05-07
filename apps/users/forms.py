# apps/users/forms.py  —  ПОЛНЫЙ ФАЙЛ (заменить существующий)

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Никнейм",
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Введите никнейм",
            "autocomplete": "username",
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Введите пароль",
            "autocomplete": "current-password",
        })
    )


class RegisterForm(forms.ModelForm):
    ROLE_CHOICES = [
        (User.Role.STUDENT, "Ученик"),
        (User.Role.PARENT,  "Родитель"),
        (User.Role.MENTOR,  "Ментор"),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Я регистрируюсь как",
        widget=forms.RadioSelect(attrs={"class": "role-radio"}),
        initial=User.Role.STUDENT,
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Придумайте пароль",
            "autocomplete": "new-password",
        })
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Повторите пароль",
            "autocomplete": "new-password",
        })
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "role"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "auth-input", "placeholder": "Имя"}),
            "last_name":  forms.TextInput(attrs={"class": "auth-input", "placeholder": "Фамилия"}),
            "username":   forms.TextInput(attrs={"class": "auth-input", "placeholder": "Никнейм"}),
            "email":      forms.EmailInput(attrs={"class": "auth-input", "placeholder": "Email"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name":  "Фамилия",
            "username":   "Никнейм",
            "email":      "Email",
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1", "")
        p2 = self.cleaned_data.get("password2", "")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        validate_password(p2)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# ─────────────────────────────────────────────────────────
#  Формы редактирования профиля
# ─────────────────────────────────────────────────────────
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Имя"}),
            "last_name":  forms.TextInput(attrs={"class": "profile-input", "placeholder": "Фамилия"}),
            "email":      forms.EmailInput(attrs={"class": "profile-input", "placeholder": "Email"}),
            "phone":      forms.TextInput(attrs={"class": "profile-input", "placeholder": "Телефон"}),
            "avatar":     forms.FileInput(attrs={"class": "profile-input", "accept": "image/*"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
            "phone": "Телефон",
            "avatar": "Аватар",
        }


class StudentProfileForm(forms.ModelForm):
    class Meta:
        from apps.students.models import Student
        model = Student
        fields = ["birth_date", "education_level", "interests", "study_status"]
        widgets = {
            "birth_date":      forms.DateInput(format="%Y-%m-%d", attrs={"class": "profile-input", "type": "date"}),
            "education_level": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Класс / уровень"}),
            "interests":       forms.Textarea(attrs={"class": "profile-input", "rows": 3, "placeholder": "Ваши интересы"}),
            "study_status":    forms.TextInput(attrs={"class": "profile-input", "placeholder": "Статус обучения"}),
        }
        labels = {
            "birth_date": "Дата рождения",
            "education_level": "Уровень образования",
            "interests": "Интересы",
            "study_status": "Статус обучения",
        }


class MentorProfileForm(forms.ModelForm):
    class Meta:
        from apps.mentors.models import Mentor
        model = Mentor
        fields = ["specialization", "experience_years", "bio"]
        widgets = {
            "specialization":   forms.TextInput(attrs={"class": "profile-input", "placeholder": "Специализация"}),
            "experience_years": forms.NumberInput(attrs={"class": "profile-input", "placeholder": "Лет опыта"}),
            "bio":              forms.Textarea(attrs={"class": "profile-input", "rows": 4, "placeholder": "О себе"}),
        }
        labels = {
            "specialization": "Специализация",
            "experience_years": "Опыт работы (лет)",
            "bio": "О себе",
        }


class ParentProfileForm(forms.ModelForm):
    class Meta:
        from apps.students.models import Parent
        model = Parent
        fields = ["relation_degree"]
        widgets = {
            "relation_degree": forms.TextInput(attrs={"class": "profile-input", "placeholder": "Степень родства"}),
        }
        labels = {
            "relation_degree": "Степень родства",
        }