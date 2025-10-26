from django.urls import path, register_converter

from . import views
from . import views_partial
from planer_app.converters import DateConverter

register_converter(DateConverter, "date")

urlpatterns = [
    path("", views.index, name="index"),
    path("expenses/", views.expenses, name="expenses"),
    path("gallery/", views.gallery, name="gallery"),
    path("tasks_manage/", views.tasks_manage, name="tasks_manage"),
    path("users_manage/", views.users_manage, name="users_manage"),
    path("tasks_manage/week/<date:date>", views.week_details, name="week_details"),
    path("reports/", views.reports, name="reports"),
    path(
        "expenses/show_pay_purchase/<int:purchase_id>",
        views_partial.show_pay_purchase,
        name="show_pay_purchase",
    ),
    path(
        "tasks_manage/show_generate_weeks",
        views_partial.show_generate_weeks,
        name="show_generate_weeks",
    ),
    path(
        "tasks_manage/week/show_edit_task/<int:task_id>/<int:week_id>",
        views_partial.show_edit_task,
        name="show_edit_task",
    ),
    path(
        "tasks_manage/week/show_add_task/<int:week_id>",
        views_partial.show_add_task,
        name="show_add_task",
    ),
]
