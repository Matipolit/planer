from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Task(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    frequency = models.IntegerField(default=1)

def validate_date_range(start_date, end_date):
    if start_date > end_date:
        raise ValidationError("The end date must be greater or equal than the start date.")

class Week(models.Model):

    #no mask for now
    start_date = models.DateField(unique=True, null=False, blank=False)
    end_date = models.DateField(unique=True, null=False, blank=False, validators=[validate_date_range])

class Purchase(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
    amount = models.IntegerField(default=1)
    #basic user for now
    locator_id = models.ForeignKey(User, on_delete=models.CASCADE)

class Debt(models.Model):
    purchase_id = models.OneToOneField(Purchase, on_delete=models.CASCADE, null=False, blank=False)
    # basic user for now
    locator_id = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    is_paid = models.BooleanField(default=False, null=False, blank=False)

class TasksInWeek(models.Model):
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, null=False, blank=False)
    week_id = models.ForeignKey(Week, on_delete=models.CASCADE, null=False, blank=False)
    locator_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    is_done = models.BooleanField(default=False, null=False, blank=False)
