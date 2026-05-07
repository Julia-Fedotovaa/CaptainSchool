# apps/users/urls.py  —  ПОЛНЫЙ ФАЙЛ (заменить существующий)

from django.urls import path
from .views import (
    UserLoginView, UserLogoutView, RegisterView,
    HomeRedirectView,
    AdminDashboardView, MentorDashboardView,
    ParentDashboardView, StudentDashboardView,
    ProfileEditView, AboutView, ServicesView,
    HelpView, FaqView, PrivacyView, TermsView,
    home, all_courses, contact_submit,
)

urlpatterns = [
    path("login/",    UserLoginView.as_view(),  name="login"),
    path("logout/",   UserLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(),   name="register"),

    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),

    path("courses/",  all_courses,              name="all_courses"),

    path("admin-dashboard/", AdminDashboardView.as_view(),   name="admin_dashboard"),
    path("mentor/",          MentorDashboardView.as_view(),  name="mentor_dashboard"),
    path("parent/",          ParentDashboardView.as_view(),  name="parent_dashboard"),
    path("student/",         StudentDashboardView.as_view(), name="student_dashboard"),

    path("about/",    AboutView.as_view(),    name="about"),
    path("services/", ServicesView.as_view(), name="services"),
    path("help/",     HelpView.as_view(),     name="help"),
    path("faq/",      FaqView.as_view(),      name="faq"),
    path("privacy/",  PrivacyView.as_view(),  name="privacy"),
    path("terms/",    TermsView.as_view(),    name="terms"),

    path("contact/", contact_submit, name="contact_submit"),

    path("", home, name="home"),
]