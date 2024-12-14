from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm


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

