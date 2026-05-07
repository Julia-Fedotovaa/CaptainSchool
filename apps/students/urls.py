from django.urls import path
from .views import (
    ParentChildrenListView,
    ParentChildCoursesView,
    ParentChildScheduleView,
    AddChildView,
    ChildCredentialsView,
    ParentChildEditView,
)

urlpatterns = [
    path("parent/children/", ParentChildrenListView.as_view(), name="parent_children"),
    path("parent/children/<int:student_id>/courses/", ParentChildCoursesView.as_view(), name="parent_child_courses"),
    path("parent/children/<int:student_id>/schedule/", ParentChildScheduleView.as_view(), name="parent_child_schedule"),
    path("parent/children/<int:student_id>/edit/", ParentChildEditView.as_view(), name="parent_child_edit"),
    path("parent/children/add/", AddChildView.as_view(), name="parent_add_child"),
    path("parent/children/<int:student_id>/credentials/", ChildCredentialsView.as_view(), name="child_credentials"),
]
