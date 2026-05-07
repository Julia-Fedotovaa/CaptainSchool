from django.urls import path
from .views import (
    ProgressListView, ProgressCreateView, ProgressUpdateView,
    StudentProgressView, ParentChildProgressView,
)

urlpatterns = [
    # admin / mentor
    path("", ProgressListView.as_view(), name="progress_list"),
    path("create/", ProgressCreateView.as_view(), name="progress_create"),
    path("<int:pk>/edit/", ProgressUpdateView.as_view(), name="progress_edit"),

    # student
    path("my/", StudentProgressView.as_view(), name="student_progress"),

    # parent
    path("parent/<int:student_id>/", ParentChildProgressView.as_view(), name="parent_child_progress"),
]
