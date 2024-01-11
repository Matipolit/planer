from typing import Any, Type

from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Task, User, TasksInWeek, Week, Purchase, Debt
import json
from datetime import date, timedelta, datetime


# for iterating over time by week
def dateSpan(startDate, endDate, delta=timedelta(weeks=1)):
    currentDate = startDate
    idx = 0
    while currentDate < endDate:
        yield (currentDate, idx)
        idx += 1
        currentDate += delta


# views
@login_required(login_url='login')
def index(request: HttpRequest):
    today_date = date.today()
    monday_date = today_date - timedelta(days=today_date.weekday())

    week = None

    try:
        week = Week.objects.get(start_date=monday_date + timedelta(weeks=1))
        tasks = TasksInWeek.objects.all().filter(week_id=week)
    except Exception:
        pass

    if week == None or tasks == None:
        return render(request, "index.html")

    if request.method == "POST":
        for task_id, is_done in request.POST.items():
            if task_id == "csrfmiddlewaretoken":
                continue
            # print(task_id)
            # print(is_done)
            task = Task.objects.all().filter(id=task_id)
            if task:
                instance = tasks.get(task_id=task[0])
                if is_done == "on":
                    instance.is_done = True
                else:
                    instance.is_done = False
                instance.save()

    users = []

    for task in list(tasks):
        # print(str(task.is_done))
        users.append(str(task.locator_id.username))

    users = set(users)
    users = list(users)

    context = {"tasks": tasks, "users": users}

    # print(str(context["tasks"][0]))

    return render(request, "index.html", context)

def get_my_debts_by_person(all_debts, user):
    my_debts = all_debts.filter(locator_id=user, is_paid=False)
    my_debts_by_person = dict()
    for debt in my_debts:
        if debt.purchase_id.locator_id not in my_debts_by_person:
            my_debts_by_person[debt.purchase_id.locator_id] = {"sum": 0, "debts": []}
        my_debts_by_person[debt.purchase_id.locator_id]["sum"] += debt.owed_by_locator(all_debts)
        my_debts_by_person[debt.purchase_id.locator_id]["debts"].append(debt)
    return my_debts_by_person

@login_required(login_url='login')
def expenses(request: HttpRequest):
    my_debts_by_person = get_my_debts_by_person(Debt.objects.all(), request.user)

    if (request.method == "POST"):
        vars = request.POST
        type = vars["formtype"]
        if (type == "to_purchase"):
            Purchase.objects.create(name=vars["name"], price=vars["price"], amount=vars["amount"])
        elif (type == "purchased"):
            purchase = Purchase.objects.get(id=vars["purchase_id"])
            indebted: Type[QueryDict[int]] = vars["indebted"]

            purchase.locator_id = request.user
            purchase.save()

            for id in indebted:
                Debt.objects.create(purchase_id=purchase, locator_id=User.objects.get(id=id), is_paid=False)
        elif (type == "pay_all_debts"):
            debts_to_pay = my_debts_by_person[User.objects.get(id=vars["locator_id"])]["debts"]
            for debt in debts_to_pay:
                debt.is_paid = True
                debt.save()

            my_debts_by_person = get_my_debts_by_person(Debt.objects.all(), request.user)

    to_purchase = Purchase.objects.filter(locator_id=None)

    users = User.objects.exclude(id=request.user.id)
    context = {'to_purchase': to_purchase, 'debts': my_debts_by_person, 'user': request.user, 'users': users}

    return render(request, "expenses.html", context)


@staff_member_required(login_url="login")
def tasks_manage(request):
    errors = []
    if (request.method == "POST"):
        vars = request.POST
        type = vars["formtype"]

        if (type == "task"):
            Task.objects.create(name=vars["name"], frequency=vars["frequency"])
        elif (type == "generate"):

            tasks = Task.objects.all()
            if vars["beg_date"] == "" or vars["end_date"] == "":
                errors.append("Dates not selected. Please fill in all the fields")
            else:
                begDate = datetime.strptime(vars["beg_date"], "%Y-%m-%d")
                endDate = datetime.strptime(vars["end_date"], "%Y-%m-%d")

                includeAdminInTasks = "include_admin" in vars.keys()
                if (includeAdminInTasks):
                    locators = User.objects.all()
                else:
                    locators = User.objects.all().exclude(is_superuser=True)
                locatorsNum = len(locators)
                for (weekBegDate, idx) in dateSpan(begDate, endDate):
                    weekEndDate: datetime.date = weekBegDate + timedelta(days=6)
                    print(f"Generating week {weekBegDate} - {weekEndDate}")
                    week = Week.objects.create(start_date=weekBegDate, end_date=weekEndDate)
                    print("week generated")
                    for task in tasks:
                        print(f"Checking to add task {task} with freq {task.frequency} and idx of week {idx}")
                        if (idx % task.frequency == 0):
                            print(f"Task elegible to add")
                            taskInWeek = TasksInWeek.objects.create(locator_id=locators[idx % locatorsNum],
                                                                    task_id=task,
                                                                    week_id=week, is_done=False)
                            print(taskInWeek)

    elif (request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        type = vars["type"]
        if (type == "task"):
            instance = Task.objects.get(id=id)
        elif (type == "week"):
            instance = Week.objects.get(id=id)
            TasksInWeek.objects.all().filter(week_id=instance.id).delete()

        print(f"Deleting instance {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})

    today_date = date.today()
    monday_date = today_date - timedelta(days=today_date.weekday())
    tasks = Task.objects.all()
    weeks = Week.objects.all()
    for week in weeks:
        tasksInWeek = TasksInWeek.objects.all().filter(week_id=week.id)
        week.count = len(tasksInWeek)
    context = {"tasks": tasks, "today": monday_date.strftime("%Y-%m-%d"), "weeks": weeks, "errors": errors}
    return render(request, "tasks_manage.html", context)


@staff_member_required(login_url="login")
def week_details(request, date):
    errors = []
    if request.method == "DELETE":
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = TasksInWeek.objects.get(id=id)
        if instance is None:
            errors.append("Could not delete - no suchtask in week")
        else:
            print(f"Deleting instance {instance}")
            instance.delete()
            return JsonResponse({"deleted": "true"})
    elif request.method == "POST":
        vars = request.POST
        week = Week.objects.get(start_date=date)
        task = Task.objects.get(id=vars["task"])
        locator = User.objects.get(id=vars["locator"])
        TasksInWeek.objects.create(week_id=week, task_id=task, locator_id=locator, is_done=False)

    week = Week.objects.get(start_date=date)
    tasks = TasksInWeek.objects.filter(week_id=week.id)
    taskIdsInWeek = tasks.values_list("task_id")
    tasksNotInWeek = Task.objects.exclude(id__in=taskIdsInWeek)
    context = {"tasks": tasks, "week": week, "tasksNotInWeek": tasksNotInWeek, 'locators': User.objects.all()}
    return render(request, "week.html", context)


@staff_member_required(login_url="login")
def users_manage(request):
    if (request.method == "POST"):
        vars = request.POST
        User.objects.create_user(is_superuser="admin" in vars.keys(),
                                 email=vars["email"],
                                 username=vars["username"],
                                 first_name=vars["first_name"],
                                 last_name=vars["last_name"],
                                 password=vars["password"])

    elif (request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = User.objects.get(id=id)
        print(f"Deleting user {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})

    users = User.objects.all()
    context = {"users": users}
    return render(request, "users_manage.html", context)
