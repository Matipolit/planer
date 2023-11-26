from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Task


@login_required(login_url='login')
def index(request: HttpRequest):
    context = {"user_name": request.user.first_name}
    return render(request, "index.html", context)


@login_required(login_url='login')
def expenses(request: HttpRequest):
    context = {"user_name": request.user.first_name}
    return render(request, "expenses.html", context)


@staff_member_required(login_url="login")
def tasks_manage(request: HttpRequest):
    if(request.method == "POST"):
        vars = request.POST
        instance = Task.objects.create(name = vars["name"], frequency = vars["frequency"])
        print(f"Manage tasks instance: {instance}")

    tasks = Task.objects.all()
    print(f"tasks: {tasks}")
    context = {"user_name": request.user.first_name, "tasks": tasks}
    return render(request, "tasks_manage.html", context)
