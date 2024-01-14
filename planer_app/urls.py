from django.urls import path, register_converter

from . import views
from planer_app.converters import DateConverter

register_converter(DateConverter, 'date')

urlpatterns = [
    path("", views.index, name="index"),
    path("expenses/", views.expenses, name="expenses"),
    path("tasks_manage/", views.tasks_manage, name="tasks_manage"),
    path("users_manage/", views.users_manage, name="users_manage"),
    path("tasks_manage/week/<date:date>", views.week_details, name="week_details"),
    path("reports/", views.reports, name="reports"),
]
