from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def index(request: HttpRequest):
    context = {"user_name": request.user.first_name}
    return render(request, "index.html", context)


@login_required(login_url='login')
def expenses(request: HttpRequest):
    context = {"user_name": request.user.first_name}
    return render(request, "expenses.html", context)

