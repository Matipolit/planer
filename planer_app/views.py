from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

def login(request):
    return HttpResponse(request)


