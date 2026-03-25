from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserEditForm
from django.contrib import messages
from django.contrib import messages # Import this at the top

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Send a success message to the template
            messages.success(request, 'Your profile has been successfully updated!')
            return redirect('network:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
        
    return render(request, 'accounts/edit_profile.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('/') 

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('network:profile', username=user.username)
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('network:profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
        
    return render(request, 'accounts/edit_profile.html', {'form': form})