from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path, include, reverse_lazy
from django.conf import settings
from planer_app import views
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import redirect

URL_PREFIX = getattr(settings, "URL_PREFIX", "planer")


def logout_view(request):
    logout(request)
    return redirect("/planer/login")


urlpatterns = [
    path(f"{URL_PREFIX}/", include("planer_app.urls")),
    path(f"{URL_PREFIX}/admin/", admin.site.urls),
    path(
        f"{URL_PREFIX}/login/",
        LoginView.as_view(template_name="login.html", next_page=f"/{URL_PREFIX}/"),
        name="login",
    ),
    path(f"{URL_PREFIX}/logout/", logout_view, name="logout"),
]
