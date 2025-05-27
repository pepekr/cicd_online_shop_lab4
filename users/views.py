from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from users.forms.CustomCreationForm import CustomUserCreationForm
from users.forms.EmailLoginForm import EmailLoginForm


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("/")
        else:
            # When form invalid, re-render with errors
            return render(request, "registration.html", {"form": form})
    else:
        form = CustomUserCreationForm()
    return render(request, "registration.html", {"form": form})


def login_view(request):
    form = EmailLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.user)
        return redirect("/")
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("/login/")
