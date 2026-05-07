from django.urls import path
from .views import (
    TrajectoryListView, TrajectoryCreateView, TrajectoryUpdateView,
    StudentTrajectoryView, ParentChildTrajectoryView,
    GenerateTrajectoryView,
)

urlpatterns = [
    # admin / mentor
    path("", TrajectoryListView.as_view(), name="trajectory_list"),
    path("create/", TrajectoryCreateView.as_view(), name="trajectory_create"),
    path("<int:pk>/edit/", TrajectoryUpdateView.as_view(), name="trajectory_edit"),

    # student
    path("my/", StudentTrajectoryView.as_view(), name="student_trajectory"),

    # parent
    path("parent/<int:student_id>/", ParentChildTrajectoryView.as_view(), name="parent_child_trajectory"),

    # auto-generation from placement test
    path("generate/", GenerateTrajectoryView.as_view(), name="generate_trajectory"),
]
