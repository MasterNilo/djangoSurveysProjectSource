from django.contrib import admin

from surveys.models import Answer
from surveys.models import Option
from surveys.models import Question
from surveys.models import Submission
from surveys.models import Survey


class AnswerInline(admin.TabularInline):
    model = Answer


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['status', 'survey', ]
    inlines = [AnswerInline]


class OptionInline(admin.TabularInline):
    model = Option


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'type', 'survey', ]
    inlines = [OptionInline]


class QuestionInline(admin.TabularInline):
    model = Question


class SurveyAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'status', ]
    list_filter = ['author', 'status', 'date_created', ]
    ordering = ('status', 'date_created',)
    raw_id_fields = ('author',)
    inlines = [QuestionInline]


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)
