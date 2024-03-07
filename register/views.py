from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from register.forms import UserForm, LoginForm
from django.contrib.auth.models import Group, User


def register(request):
    """
    View function to handle the registration of a new user

    :param request:
    :return:
    """
    # If the request method is POST, user has submitted the form
    if request.method == 'POST':
        # Declares a form and adds the data from the form
        form = UserForm(request.POST)
        # Checks if the form is valid
        if form.is_valid():
            form.save()  # This will save the User and create an Account

            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            # Redirects the user to the home page after registration
            messages.success(request, "You have been registered and you have been automatically logged in.")
            return redirect('home')
        # If form is not valid, return the form with the errors
        else:
            messages.error(request, "Invalid information")
            context = {'form': form, 'admin': False}
            return render(request, 'register/register.html', context)
    # Otherwise, render an empty form
    else:
        form = UserForm()  # Instantiate an empty form for GET request
        context = {'form': form, 'admin': False}
        return render(request, 'register/register.html', context)


def login_view(request):
    """
    View function to handle the login of a user

    :param request:
    :return:
    """
    # If the request method is POST, user has submitted the form
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # Checks if the form is valid
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticates the user
            user = authenticate(request, username=username, password=password)
            # If the user is authenticated, log the user in and redirect to home page
            if user is not None:
                login(request, user)
                messages.success(request, "You have been logged in")
                if user.groups.filter(name="AdminGroup").exists():
                    messages.success(request, "You are an admin and can view all transaction and users "
                                              "as well as register new admins.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
                return render(request, 'register/login.html', {'form': form})
        else:
            form = LoginForm()
            messages.error(request, "Invalid information")
            return render(request, 'register/login.html', {'form': form})
    else:
        form = LoginForm()
        return render(request, 'register/login.html', {'form': form})
