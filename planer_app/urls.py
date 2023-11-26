from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("expenses/", views.expenses, name="expenses"),
    path("tasks_manage/", views.tasks_manage, name="tasks_manage")
]
