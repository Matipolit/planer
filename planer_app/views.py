from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Task, User
import json 
from datetime import date, timedelta, datetime

@login_required(login_url='login')
def index(request: HttpRequest):
    return render(request, "index.html")


@login_required(login_url='login')
def expenses(request: HttpRequest):
    return render(request, "expenses.html")


@staff_member_required(login_url="login")
def tasks_manage(request):
    if(request.method == "POST"):
        vars = request.POST
        type = vars["formtype"]

        if(type=="task"):
            Task.objects.create(name = vars["name"], frequency = vars["frequency"])
        elif(type=="generate"):
            endDate = datetime.strptime(vars["end_date"], "%Y-%m-%d")
            print(endDate)

    elif(request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = Task.objects.get(id=id)
        print(f"Deleting instance {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})

    today_date = date.today()
    monday_date = today_date - timedelta(days = today_date.weekday())
    tasks = Task.objects.all()
    context = {"tasks": tasks, "today": monday_date.strftime("%Y-%m-%d")}
    return render(request, "tasks_manage.html", context)

@staff_member_required(login_url="login")
def users_manage(request):
    if(request.method == "POST"):
        vars = request.POST
        User.objects.create(is_superuser = "admin" in vars.keys(),
            email = vars["email"],
            username=vars["username"],
            first_name=vars["first_name"],
            last_name=vars["last_name"],
            password=vars["password"])
    elif(request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = User.objects.get(id=id)
        print(f"Deleting user {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})
    
    users = User.objects.all()
    context = {"users": users}
    return render(request, "users_manage.html", context)
