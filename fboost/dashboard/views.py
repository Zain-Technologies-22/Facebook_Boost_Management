from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm
from accounts.models import CustomUser

def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

# You can remove dashboard_home since it's replaced by dashboard_view
# def dashboard_home(request):
#     return render(request, 'dashboard/index.html')

@login_required
def campaigns(request):
    return render(request, 'dashboard/campaigns.html')

@login_required
def credits(request):
    return render(request, 'dashboard/credits.html')

@login_required
def profile(request):
    return render(request, 'dashboard/profile.html')

@login_required
def settings(request):
    return render(request, 'dashboard/settings.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})