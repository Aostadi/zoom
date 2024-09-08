from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods
from account.models import *
from account.forms import SignUpForm, LoginForm, TeamForm


@require_GET
def home(request):
    if request.user.account.team and request.user.is_authenticated:
        return render(request, 'home.html', {"team": request.user.account.team.name})
    else:
        return render(request, 'home.html', {"team": None})


def signup(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('team')
        else:
            return redirect('signup')
    else:
        return render(request, 'signup.html', {'form':form})


@require_http_methods(['GET', 'POST'])
def login_account(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                user=form.cleaned_data['user'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('login')
    else:
        return render(request, 'login.html', {'form': form})


@require_GET
def logout_account(request):
    logout(request)
    return redirect('login')



@login_required
@require_http_methods(['GET', 'POST'])
def joinoradd_team(request):
    if request.method == 'GET':
        if request.user.account.team:
            return redirect('home')
        else:
            form = TeamForm()
            return render(request, 'team.html', {'form':form})
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team_exist = Team.objects.filter(name__exact=form.cleaned_data['name']).exists()
            if team_exist:
                team = team_exist
            else:
                jitsi_path = "http://meet.jit.si/" + form.cleaned_data['name']
                team = form.save()
                team.jitsi_url_path = jitsi_path
                team.save()
            request.user.account.team = team
            request.user.account.save()
            return redirect('home')
        else:
            return redirect('team')

@require_GET
@login_required
def exit_team(request):
    request.user.account.team = None
    request.user.account.save()
    return redirect('home')