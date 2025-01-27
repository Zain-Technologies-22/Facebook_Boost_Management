# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .forms import SignUpForm
from .models import AdAccount, LoginHistory
from .forms import ApplyAdAccountForm, TransferAdAccountForm
from .forms import ProfileForm 
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group


@login_required
def apply_ad_account(request):
    if request.method == 'POST':
        form = ApplyAdAccountForm(request.POST)
        print("Form submitted")
        if form.is_valid():
            try:
                ad_account = form.save(commit=False)
                ad_account.user = request.user
                # Set payment_confirmed to True as per your logic
                ad_account.payment_confirmed = True
                # No need to set terms_conditions_agreed here
                ad_account.save()  # Removed force_insert=True to allow Django to handle it
                messages.success(request, "AD Account application submitted successfully!")
                return redirect('my_ad_account')
            except Exception as e:
                print(f"Error saving form: {str(e)}")
                messages.error(request, f"Error processing your application: {str(e)}")
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = ApplyAdAccountForm()
    return render(request, 'accounts/apply_ad_account.html', { 'form': form })

@login_required
def my_ad_account(request):
    ad_accounts = AdAccount.objects.filter(user=request.user)
    return render(request, 'accounts/my_ad_account.html', {'ad_accounts': ad_accounts})

@login_required
def transfer_ad_account(request):
    if request.method == 'POST':
        form = TransferAdAccountForm(request.POST, user=request.user)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.from_user = request.user
            transfer.save()
            messages.success(request, "AD Account transferred successfully.")
            return redirect('my_ad_account')
    else:
        form = TransferAdAccountForm(user=request.user)
    return render(request, 'accounts/transfer_ad_account.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'accounts/settings.html', {
        'form': form
    })


@login_required
def settings_view(request):
    if request.method == 'POST':
        if 'old_password' in request.POST:  # Changed from 'current_password' to 'old_password'
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                # Update session to prevent logout
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password updated successfully!')
        else:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
    
    context = {
        'form': ProfileForm(instance=request.user.profile),
        'password_form': PasswordChangeForm(request.user),
        'login_history': LoginHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]
    }
    return render(request, 'accounts/settings.html', context)
@login_required
def profile(request):
    return render(request, 'accounts/profile.html')



def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add user to web_reg_user group
            web_reg_group = Group.objects.get(name='web_reg_user')
            user.groups.add(web_reg_group)

            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})