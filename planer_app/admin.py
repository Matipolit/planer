from django.contrib import admin
from .models import Task, Debt, Purchase, TasksInWeek, Week, UserProfile, GalleryPhoto
# Register your models here.

admin.site.register(Task)
admin.site.register(Week)
admin.site.register(TasksInWeek)
admin.site.register(Purchase)
admin.site.register(Debt)
admin.site.register(UserProfile)
admin.site.register(GalleryPhoto)
