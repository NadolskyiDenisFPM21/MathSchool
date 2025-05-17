# views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from .forms import StudentRegistrationForm
from .models import User, Invite


def register_teacher(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.TEACHER
            user.save()
            return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('Main:home')
        form = UserCreationForm()
    return render(request, 'registration/register_teacher.html', {'form': form})


def register_student(request, code):
    invite = get_object_or_404(Invite, code=code, is_used=False)
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT
            user.teacher = invite.created_by
            user.save()
            invite.is_used = True
            invite.save()
            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'registration/register_student.html', {'form': form})

@login_required
def invite_list_create(request):
    if request.user.role != 'teacher':
        return redirect('login')  # или выдать 403

    if request.method == 'POST':
        Invite.objects.create(created_by=request.user)

    invites = Invite.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'teacher/invites.html', {
        'invites': invites,
    })