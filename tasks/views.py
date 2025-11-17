from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from tasks.models import *
from tasks.forms import TaskForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.core.paginator import Paginator
from django.utils import timezone

# Create your views here.
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status="Completed").count()
    pending_tasks = tasks.filter(status="Pending").count()

    context = {
        'user': request.user,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'tasks/profile.html', context)

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    q = request.GET.get('q')
    if q:
        tasks = tasks.filter(title__icontains=q)

    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)

    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)

    paginator = Paginator(tasks, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'page_obj': page_obj,
        'today': timezone.now().date(),
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.status == "Completed":
        task.status = "Pending"
        messages.info(request, "Task marked as pending.")
    else:
        task.status = "Completed"
        messages.success(request, "Task marked as completed!")
    task.save()
    return redirect('task_list')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirect to login page
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def custom_logout(request):
    logout(request)  # logs out the user
    messages.success(request, "You have been logged out successfully.")  # ✅ message here
    return redirect('login')  # redirect to login page

class LogoutWithMessageView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully.")  # ✅ message here
        return super().dispatch(request, *args, **kwargs)
