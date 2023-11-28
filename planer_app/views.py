from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Task, User
import json 


@login_required(login_url='login')
def index(request: HttpRequest):
    context = {"user_name": request.user.first_name}
    return render(request, "index.html", context)


@login_required(login_url='login')
def expenses(request: HttpRequest):
    context = {"user_name": request.user.first_name}
    return render(request, "expenses.html", context)


@staff_member_required(login_url="login")
def tasks_manage(request):
    if(request.method == "POST"):
        vars = request.POST
        Task.objects.create(name = vars["name"], frequency = vars["frequency"])
    elif(request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = Task.objects.get(id=id)
        print(f"Deleting instance {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})
    tasks = Task.objects.all()
    context = {"tasks": tasks}
    return render(request, "tasks_manage.html", context)


@staff_member_required(login_url="login")
def users_manage(request):
    if(request.method == "POST"):
        vars = request.POST
        print(vars)
        if("admin" in vars.keys()):
            print("admin")
        User.objects.create(is_superuser = "admin" in vars.keys(),
                             email = vars["email"],
                            username=vars["username"],
                            first_name=vars["first_name"],
                            last_name=vars["last_name"],
                            password=vars["password"])
    users = User.objects.all()
    context = {"users": users}
    return render(request, "users_manage.html", context)
