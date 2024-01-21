from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Task, User, TasksInWeek, Week, Purchase, Debt
from datetime import datetime, timedelta, date

@login_required(login_url='login')
def show_pay_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    users = User.objects.exclude(id=request.user.id)
    context = {
        'purchase': purchase,
        'users': users,
    }
    return render(request, "partial/pay_purchase.html", context)


@staff_member_required(login_url='login')
def show_generate_weeks(request):
    today_date = date.today()
    monday_date = today_date - timedelta(days=today_date.weekday())

    if Week.objects.count() == 0:
        context = {
            'nextWeekStart': monday_date.strftime("%Y-%m-%d"),
            'nextNextWeekStart': (monday_date + timedelta(days=7)).strftime("%Y-%m-%d"),
            "today": monday_date.strftime("%Y-%m-%d"),
        }
        return render(request, "partial/generate_weeks.html", context)

    last_generated_week = Week.objects.order_by("start_date").last()
    next_week_start = last_generated_week.end_date + timedelta(days=1)
    next_next_week_start = next_week_start + timedelta(days=7)
    context = {
        'nextWeekStart': next_week_start.strftime("%Y-%m-%d"),
        'nextNextWeekStart': next_next_week_start.strftime("%Y-%m-%d"),
        "today": monday_date.strftime("%Y-%m-%d"),
    }
    return render(request, "partial/generate_weeks.html", context)


@staff_member_required(login_url='login')
def show_edit_task(request, task_id, week_id):
    taskInWeek = get_object_or_404(TasksInWeek, pk=task_id)
    locators = User.objects.all().order_by("first_name", "last_name")
    tasksNotInWeek = Task.objects.exclude(tasksinweek__week_id=week_id).order_by("name")
    allTasks = Task.objects.all().order_by("name")
    context = {
        'taskInWeek': taskInWeek,
        'locators': locators,
        'tasksNotInWeek': tasksNotInWeek,
        'allTasks': allTasks,
    }
    return render(request, "partial/edit_task.html", context)

@staff_member_required(login_url='login')
def show_add_task(request, week_id):
    locators = User.objects.all().order_by("first_name", "last_name")
    tasksNotInWeek = Task.objects.exclude(tasksinweek__week_id=week_id).order_by("name")
    context = {
        'locators': locators,
        'tasksNotInWeek': tasksNotInWeek,
    }
    return render(request, "partial/add_task.html", context)