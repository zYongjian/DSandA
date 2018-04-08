from django.contrib import admin
from .models import *


# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['school']
    list_display = ('name', 'student_id', 'school')


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    search_fields = ['student__name']
    list_filter = ["homework__name"]
    list_display = ('homework_name', 'student_id', 'student_name', 'assistant_name')
    ordering = ["-time"]

    def homework_name(self, obj):
        return obj.homework.name

    def student_id(self, obj):
        return obj.student.student_id

    def student_name(self, obj):
        return obj.student.name

    def assistant_name(self, obj):
        return obj.assistant.name


@admin.register(Homework)
class HomeWorkAdmin(admin.ModelAdmin):
    list_display = ('name', 'cutoff')


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'student_id')


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    search_fields = ['student__name']
    list_filter = ['homework__name']
    list_display = ('student_id', 'student_name', 'homework_name', 'score')

    def student_id(self, obj):
        return obj.student.student_id

    def student_name(self, obj):
        return obj.student.name

    def homework_name(self, obj):
        return obj.homework.name


admin.site.site_header = "数据结构与算法作业提交评分系统"
admin.site.site_title = "数据结构与算法作业提交评分系统"
