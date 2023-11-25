from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path, include, reverse_lazy
from planer_app import views
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return(redirect("/planer/login"))

urlpatterns = [

    path("planer/", include("planer_app.urls")),
    path("planer/admin/", admin.site.urls),
    path("planer/login/", LoginView.as_view(template_name="login.html",next_page=("/planer/")), name='login'),
    path("planer/logout/", logout_view, name="logout"),
]
