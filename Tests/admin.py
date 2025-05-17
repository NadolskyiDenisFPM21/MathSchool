from django.contrib import admin
from .models import (
    Test, Question, TextQuestion, ChoiceQuestion, MatchQuestion,
    TestAttempt, Answer
)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'author', 'test_link')
    search_fields = ('title',)
    ordering = ('-created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'test')
    list_filter = ('question_type', 'test')
    search_fields = ('text',)


@admin.register(TextQuestion)
class TextQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'correct_answer')
    search_fields = ('text',)


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'correct_choice')
    search_fields = ('text',)


@admin.register(MatchQuestion)
class MatchQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test')
    search_fields = ('text',)


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'started_at', 'finished_at')
    list_filter = ('test',)
    search_fields = ('student__username', 'test__title')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question')
    list_filter = ('question',)
    search_fields = ('attempt__student__username', 'question__text')
