from django.urls import path
from .views import (
    TrackListView, TrackCreateView, TrackUpdateView, TrackDeleteView,
    CourseListView, CourseCreateView, CourseUpdateView, CourseDeleteView,
    ScheduleListView, ScheduleCreateView, ScheduleUpdateView, ScheduleDeleteView,
    StudentCourseListView, StudentScheduleListView,
    ParentChildScheduleView, AvailableCourseListView, MyCourseListView, UnenrollCourseView, EnrollCourseView,
    PlacementTestView, PlacementTestResultView, CourseDetailView, CourseReviewView, LessonPlayerView, LessonResultView,
    LessonCardSubmitView,
    MentorSubscribeCourseView, MentorUnsubscribeCourseView, ScheduleDetailView,
    LessonEditorView, LessonCreateEditorView,
    StudentSearchAPIView,
    CourseCreateWizardView,
)

urlpatterns = [
    # ADMIN / MENTOR (управление)
    path("tracks/", TrackListView.as_view(), name="track_list"),
    path("tracks/create/", TrackCreateView.as_view(), name="track_create"),
    path("tracks/<int:pk>/edit/", TrackUpdateView.as_view(), name="track_edit"),
    path("tracks/<int:pk>/delete/", TrackDeleteView.as_view(), name="track_delete"),

    path("courses/", CourseListView.as_view(), name="course_list"),
    path("courses/create/", CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/edit/", CourseUpdateView.as_view(), name="course_edit"),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view(), name="course_delete"),

    path("schedule/", ScheduleListView.as_view(), name="schedule_list"),
    path("schedule/create/", ScheduleCreateView.as_view(), name="schedule_create"),
    path("schedule/<int:pk>/edit/", ScheduleUpdateView.as_view(), name="schedule_edit"),
    path("schedule/<int:pk>/delete/", ScheduleDeleteView.as_view(), name="schedule_delete"),

    # STUDENT (просмотр)
    path("my/courses/", StudentCourseListView.as_view(), name="student_courses"),
    path("my/schedule/", StudentScheduleListView.as_view(), name="student_schedule"),

    # PARENT (просмотр расписания ребёнка; пока упрощённо)
    path("parent/child/schedule/", ParentChildScheduleView.as_view(), name="parent_child_schedule"),

    path("available/", AvailableCourseListView.as_view(), name="available_courses"),
    path("my/", MyCourseListView.as_view(), name="my_courses"),
    path("enroll/<int:course_id>/", EnrollCourseView.as_view(), name="enroll_course"),
    path("unenroll/<int:course_id>/", UnenrollCourseView.as_view(), name="unenroll_course"),

    path("placement-test/", PlacementTestView.as_view(), name="placement_test_start"),
    path("placement-test/result/<int:session_id>/", PlacementTestResultView.as_view(), name="placement_test_result"),

    path("courses/<int:course_id>/",             CourseDetailView.as_view(),    name="course_detail"),
    path("courses/<int:course_id>/review/",      CourseReviewView.as_view(),    name="course_review"),
    path("lessons/<int:lesson_id>/play/",        LessonPlayerView.as_view(),    name="lesson_player"),
    path("lessons/<int:lesson_id>/submit/",      LessonCardSubmitView.as_view(),name="lesson_card_submit"),
    path("lessons/<int:lesson_id>/result/",      LessonResultView.as_view(),    name="lesson_result"),

    # Lesson editor
    path("courses/<int:course_id>/lessons/create/editor/", LessonCreateEditorView.as_view(), name="lesson_create_editor"),
    path("lessons/<int:lesson_id>/editor/",                LessonEditorView.as_view(),       name="lesson_editor"),

    # Mentor: подписка на курс
    path("courses/<int:course_id>/subscribe/",   MentorSubscribeCourseView.as_view(),   name="mentor_subscribe_course"),
    path("courses/<int:course_id>/unsubscribe/", MentorUnsubscribeCourseView.as_view(), name="mentor_unsubscribe_course"),

    # Webinar detail
    path("schedule/<int:pk>/detail/", ScheduleDetailView.as_view(), name="schedule_detail"),

    # API: поиск учеников
    path("api/students/search/", StudentSearchAPIView.as_view(), name="student_search_api"),

    # Создание курса (визард с уроками)
    path("courses/create/wizard/", CourseCreateWizardView.as_view(), name="course_create_wizard"),
]
