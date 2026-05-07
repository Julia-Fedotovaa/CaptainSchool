from django.contrib import admin

from apps.education.models import CardChoice, LessonCard, Lesson, LessonProgress


class CardChoiceInline(admin.TabularInline):
    model = CardChoice
    extra = 4
    fields = ["text", "is_correct", "order"]



class LessonCardInline(admin.StackedInline):
    model = LessonCard
    extra = 2
    fields = ["card_type", "order", "title", "content", "image"]
    show_change_link = True


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["course", "order", "title", "lesson_type", "color"]
    list_filter = ["course", "lesson_type", "color"]
    inlines = [LessonCardInline]


@admin.register(LessonCard)
class LessonCardAdmin(admin.ModelAdmin):
    list_display = ["lesson", "order", "card_type", "title"]
    list_filter = ["card_type", "lesson__course"]
    inlines = [CardChoiceInline]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["student", "lesson", "status", "correct_answers", "total_test_cards"]
    list_filter = ["status"]