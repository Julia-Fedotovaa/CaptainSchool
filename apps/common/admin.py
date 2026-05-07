from apps.common.models import ContactMessage
from apps.progress.models import Progress
from apps.trajectories.models import IndividualTrajectory
from apps.mentors.models import Mentor
from django.contrib import admin
from apps.users.models import User
from apps.education.models import Track, Course, Schedule, Enrollment, CourseReview, CourseCategory, PlacementTest, PlacementAnswer, PlacementTestSession, PlacementQuestion, ChoiceOption, MatchingPair
from apps.students.models import Student, Parent, StudentBadge, Badge, StudentStats

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ("name", "email", "short_message", "created_at", "is_read")
    list_filter   = ("is_read", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")
    list_editable = ("is_read",)
    ordering      = ("-created_at",)

    def short_message(self, obj):
        return obj.message[:60] + "…" if len(obj.message) > 60 else obj.message
    short_message.short_description = "Сообщение"


admin.site.register(Progress)
admin.site.register(IndividualTrajectory)
admin.site.register(Mentor)
admin.site.register(Track)
admin.site.register(Course)
admin.site.register(Schedule)
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Enrollment)
admin.site.register(CourseReview)
admin.site.register(CourseCategory)
admin.site.register(PlacementTest)
admin.site.register(PlacementAnswer)
admin.site.register(PlacementTestSession)
admin.site.register(PlacementQuestion)
admin.site.register(ChoiceOption)
admin.site.register(MatchingPair)
admin.site.register(Badge)
admin.site.register(StudentBadge)
admin.site.register(StudentStats)