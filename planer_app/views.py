from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Task
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
        print(f"hello from post {vars}")
        Task.objects.create(name = vars["name"], frequency = vars["frequency"])
    elif(request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = Task.objects.get(id=id)
        print(f"Deleting instance {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})
    tasks = Task.objects.all()
    context = {"user_name": request.user.first_name, "tasks": tasks}
    return render(request, "tasks_manage.html", context)
