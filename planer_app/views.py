from typing import Any, Type

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse, QueryDict
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q, Aggregate, Value, Case, When, CharField, F, OuterRef, Subquery

from .models import Task, User, TasksInWeek, Week, Purchase, Debt
import json
from datetime import date, timedelta, datetime
from planer_app.tasks import sendEmail


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
    thisWeek = None
    tasks = []
    users = None

    if request.method == "POST":
        vars = request.POST
        type = vars["formtype"]

        if type == "done":
            print(f"done vars: {vars}")
            task_id = vars["task_id"]
            is_done = vars["checked"]
            task = TasksInWeek.objects.get(id=task_id)
            if task:
                if is_done == "on":
                    print("Marking task as done")
                    task.is_done = True
                else:
                    print("Marking task as not done")
                    task.is_done = False
                task.save()
        elif type == "user":
            for old_user, new_user in vars.items():
                if old_user == "csrfmiddlewaretoken" or old_user == "formtype":
                    continue
                newUserTasks = tasks.filter(locator_id=users.get(id=old_user)).all()
                for newUserTask in newUserTasks:
                    newUserTask.locator_id = users.get(id=new_user)
                    newUserTask.save()

    today_date = date.today()
    monday_date = today_date - timedelta(days=today_date.weekday())
    my_tasks_all = TasksInWeek.objects.all().filter(locator_id=request.user)

    tasks_by_week_before = dict()
    tasks_by_week_after = dict()
    for week in Week.objects.all().order_by("-start_date"):
        tasks_in_week = my_tasks_all.filter(week_id=week.id)
        if len(tasks_in_week) == 0:
            continue

        if week.start_date < monday_date:
            if not tasks_in_week.filter(is_done=False).exists():
                continue
            tasks_by_week_before[week] = tasks_in_week

        elif week.start_date > monday_date:
            tasks_by_week_after[week] = tasks_in_week

        else:
            tasks = tasks_in_week

    try:
        thisWeek = Week.objects.get(start_date=monday_date)
        users = User.objects.all()
    except Exception as e:
        print(e)
        pass

    if thisWeek is None or tasks is None:
        return render(request, "index.html")

    print(f"Before tasks: {tasks_by_week_before}")

    context = {"tasks": tasks,
               "tasksByWeekBefore": tasks_by_week_before,
               "tasksByWeekAfter": tasks_by_week_after,
               "users": users,
               "week": thisWeek}

    return render(request, "index.html", context)


def get_my_debts_by_person(all_debts, user):
    my_debts = all_debts.filter(locator_id=user, is_paid=False)
    my_debts_by_person = dict()
    for debt in my_debts:
        if debt.purchase_id.locator_id not in my_debts_by_person:
            my_debts_by_person[debt.purchase_id.locator_id] = {"sum": 0, "debts": []}
        my_debts_by_person[debt.purchase_id.locator_id]["sum"] += debt.owed_amount
        my_debts_by_person[debt.purchase_id.locator_id]["debts"].append(debt)
    return my_debts_by_person


@login_required(login_url='login')
def expenses(request: HttpRequest):
    my_debts_by_person = get_my_debts_by_person(Debt.objects.all(), request.user)

    if (request.method == "POST"):
        vars = request.POST
        formType = vars["formtype"]
        if (formType == "to_purchase"):
            Purchase.objects.create(name=vars["name"], price=vars["price"], amount=vars["amount"])
        elif (formType == "purchased"):
            purchase = Purchase.objects.get(id=vars["purchase_id"])
            indebted = vars.getlist(key="indebted")

            purchase.locator_id = request.user
            purchase.save()
            owed_amount = purchase.sum_price / len(indebted)

            for locator_id in indebted:
                if int(locator_id) == request.user.id:
                    continue
                locator = User.objects.get(id=locator_id)

                print("indebted: " + locator_id)
                Debt.objects.create(purchase_id=purchase, locator_id=locator, is_paid=False, owed_amount=owed_amount)
                email = locator.email
                sendEmail.delay(email,
                                f"Hi {locator.first_name},\nYou have a new debt of {owed_amount}\nfor the purchase of {purchase.name}.\nPlease pay it back to {request.user.first_name} {request.user.last_name}.\nThanks,\nPlaner App",
                                f"Planer: New debt to {request.user.first_name} {request.user.last_name} ")

        elif (formType == "pay_all_debts"):
            paid_user = User.objects.get(id=vars["locator_id"])
            debts_to_pay = my_debts_by_person[paid_user]["debts"]
            for debt in debts_to_pay:
                debt.is_paid = True
                debt.save()

            email = paid_user.email
            sendEmail.delay(email,
                            f"Hi {paid_user.first_name},\n{request.user.first_name} {request.user.last_name} has paid you back for all their debts - {my_debts_by_person[paid_user]['sum']}.\nThanks,\nPlaner App",
                            f"Planer: All debts paid from {request.user.first_name} {request.user.last_name}")
            my_debts_by_person = get_my_debts_by_person(Debt.objects.all(), request.user)

    to_purchase = Purchase.objects.filter(locator_id=None)

    users = User.objects.exclude(id=request.user.id)
    context = {'to_purchase': to_purchase, 'debts': my_debts_by_person, 'user': request.user, 'users': users}

    return render(request, "expenses.html", context)


@staff_member_required(login_url="login")
def tasks_manage(request):
    errors = []
    if (request.method == "POST"):
        requestVars = request.POST
        formType = requestVars["formtype"]

        if formType == "task":
            Task.objects.create(name=requestVars["name"], frequency=requestVars["frequency"])

        elif formType == "generate":
            tasks = Task.objects.all()
            if requestVars["beg_date"] == "" or requestVars["end_date"] == "":
                errors.append("Dates not selected. Please fill in all the fields")
            else:
                begDate = datetime.strptime(requestVars["beg_date"], "%Y-%m-%d")
                endDate = datetime.strptime(requestVars["end_date"], "%Y-%m-%d")

                includeAdminInTasks = "include_admin" in requestVars.keys()
                if includeAdminInTasks:
                    locators = User.objects.all().order_by("first_name")
                else:
                    locators = User.objects.all().exclude(is_superuser=True)
                locatorsNum = len(locators)
                previousWeeks = Week.objects.all().filter(start_date__lte=begDate).order_by("-start_date")
                tasksWithTimesToGenerate = dict()
                for task in tasks:
                    tasksWithTimesToGenerate[task] = 1

                locatorIdx = 0
                if len(previousWeeks) > 0:
                    for idx, week in enumerate(previousWeeks):
                        tasksInWeek = TasksInWeek.objects.all().filter(week_id=week.id)
                        if idx == 0 and len(tasksInWeek) > 0:
                            locatorIdx = list(locators).index(tasksInWeek[0].locator_id)
                        for taskInWeek in tasksInWeek:
                            if taskInWeek.task_id.frequency != tasksWithTimesToGenerate[taskInWeek.task_id]:
                                if taskInWeek.task_id.frequency - idx > 1:
                                    tasksWithTimesToGenerate[taskInWeek.task_id] = taskInWeek.task_id.frequency - idx
                    print(f"Previous weeks found: {previousWeeks}")

                for (weekBegDate, idx) in dateSpan(begDate, endDate):
                    locatorIdx += 1
                    weekEndDate: datetime.date = weekBegDate + timedelta(days=6)
                    print(f"Generating week {weekBegDate} - {weekEndDate}")
                    week = Week.objects.create(start_date=weekBegDate, end_date=weekEndDate)
                    print("week generated")
                    for task in tasksWithTimesToGenerate.keys():
                        print(f"Checking to add task {task} with freq {task.frequency} and idx of week {idx}")
                        if tasksWithTimesToGenerate[task] == 1:
                            print(f"Task elegible to add")
                            taskInWeek = TasksInWeek.objects.create(locator_id=locators[locatorIdx % locatorsNum],
                                                                    task_id=task,
                                                                    week_id=week, is_done=False)
                            print(taskInWeek)
                            tasksWithTimesToGenerate[task] = task.frequency
                        else:
                            tasksWithTimesToGenerate[task] -= 1
                            print(f"Task not elegible to add")

    elif request.method == "DELETE":
        requestVars = json.loads(request.DELETE)
        idToDelete = requestVars["id"]
        formType = requestVars["type"]
        if formType == "task":
            instance = Task.objects.get(id=idToDelete)
        elif formType == "week":
            instance = Week.objects.get(id=idToDelete)
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
        vars = QueryDict(request.DELETE)
        print(f"Delete vars: {vars}")
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
        type = vars["formtype"]
        if type == "add":
            week = Week.objects.get(start_date=date)
            task = Task.objects.get(id=vars["task"])
            locator = User.objects.get(id=vars["locator"])
            TasksInWeek.objects.create(week_id=week, task_id=task, locator_id=locator, is_done=False)
        elif type == "edit":
            id = vars["taskId"]
            instance = TasksInWeek.objects.get(id=id)
            if instance is None:
                errors.append("Could not edit - no suchtask in week")
            else:
                task = Task.objects.get(id=vars["task"])
                locator = User.objects.get(id=vars["locator"])
                instance.task_id = task
                instance.locator_id = locator
                instance.save()

    week = Week.objects.get(start_date=date)
    tasks = TasksInWeek.objects.filter(week_id=week.id).order_by("id")
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


@staff_member_required(login_url="login")
def reports(request):
    weeksWithUsers = []

    weeks = Week.objects.annotate(
        total_tasks=Count('tasksinweek'),
        completed_tasks=Count('tasksinweek', filter=Q(tasksinweek__is_done=True)),
    ).order_by('start_date')

    for week in weeks:
        users = User.objects.filter(tasksinweek__week_id=week.id).distinct()
        weeksWithUsers.append({"week": week, "users": users})

    unpaidPurchasesWithUsers = []
    unpaidPurchases = Purchase.objects.filter(debt__is_paid=False).annotate(
        owedPerPerson=F('debt__purchase_id__price') / Count('debt__purchase_id')
    )

    for purchase in unpaidPurchases:
        users = User.objects.filter(debt__purchase_id=purchase.id, debt__is_paid=False).distinct()
        unpaidPurchasesWithUsers.append({"purchase": purchase, "users": users})

    context = {"weeks": weeksWithUsers, "purchases": unpaidPurchasesWithUsers}
    return render(request, "reports.html", context)
