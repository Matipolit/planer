from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Task, User, TasksInWeek, Week
import json 
from datetime import date, timedelta, datetime

# for iterating over time by week
def dateSpan(startDate, endDate, delta=timedelta(weeks=1)):
    currentDate = startDate
    idx = 0
    while currentDate <= endDate:
        yield (currentDate, idx)
        idx += 1
        currentDate += delta



# views
@login_required(login_url='login')
def index(request: HttpRequest):

    today_date = date.today()
    monday_date = today_date - timedelta(days = today_date.weekday())

    week = None

    try:
        week = Week.objects.get(start_date = monday_date + timedelta(weeks=1))
        tasks = TasksInWeek.objects.all().filter(week_id = week)
    except Exception:
        pass

    if week == None or tasks == None:
        return render(request, "index.html")
    
    if request.method == "POST" :
        for task_id, is_done in request.POST.items():
            if task_id == "csrfmiddlewaretoken":
                continue
            # print(task_id)
            # print(is_done)
            task = Task.objects.all().filter(id = task_id)
            if task:
                instance = tasks.get(task_id = task[0])
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


@login_required(login_url='login')
def expenses(request: HttpRequest):
    return render(request, "expenses.html")

@staff_member_required(login_url="login")
def tasks_manage(request):
    if(request.method == "POST"):
        vars = request.POST
        type = vars["formtype"]

        if(type=="task"):
            Task.objects.create(name = vars["name"], frequency = vars["frequency"])
        elif(type=="generate"):
            tasks = Task.objects.all()
            begDate = datetime.strptime(vars["beg_date"], "%Y-%m-%d")
            endDate = datetime.strptime(vars["end_date"], "%Y-%m-%d")

            locators = User.objects.all()
            locatorsNum = len(locators)
            for (weekBegDate, idx) in dateSpan(begDate, endDate):
                weekEndDate: datetime.date = weekBegDate + timedelta(days=6)
                print(f"Generating week {weekBegDate} - {weekEndDate}")
                week = Week.objects.create(start_date = weekBegDate, end_date = weekEndDate)
                print("week generated")
                for task in tasks:
                    print(f"Checking to add task {task} with freq {task.frequency} and idx of week {idx}")
                    if(idx % task.frequency== 0):
                        print(f"Task elegible to add")
                        taskInWeek = TasksInWeek.objects.create(locator_id = locators[idx % locatorsNum], task_id=task, week_id= week, is_done = False)
                        print(taskInWeek)

    elif(request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        type = vars["type"]
        if(type == "task"):
            instance = Task.objects.get(id = id)
        elif(type == "week"):
            instance = Week.objects.get(id = id)
            TasksInWeek.objects.all().filter(week_id = instance.id).delete()
            
        print(f"Deleting instance {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})

    today_date = date.today()
    monday_date = today_date - timedelta(days = today_date.weekday())
    tasks = Task.objects.all()
    weeks = Week.objects.all()
    for week in weeks:
        tasksInWeek = TasksInWeek.objects.all().filter(week_id = week.id)
        week.count = len(tasksInWeek)
    context = {"tasks": tasks, "today": monday_date.strftime("%Y-%m-%d"), "weeks": weeks}
    return render(request, "tasks_manage.html", context)

@staff_member_required(login_url="login")
def users_manage(request):
    if(request.method == "POST"):
        vars = request.POST
        User.objects.create(is_superuser = "admin" in vars.keys(),
            email = vars["email"],
            username=vars["username"],
            first_name=vars["first_name"],
            last_name=vars["last_name"],
            password=vars["password"])
    elif(request.method == "DELETE"):
        vars = json.loads(request.DELETE)
        id = vars["id"]
        instance = User.objects.get(id=id)
        print(f"Deleting user {instance}")
        instance.delete()
        return JsonResponse({"deleted": "true"})
    
    users = User.objects.all()
    context = {"users": users}
    return render(request, "users_manage.html", context)
