from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from register.forms import UserForm, LoginForm


def register(request):
    """
    View function to handle the registration of a new user

    :param request:
    :return:
    """
    # If the request method is POST, user has submitted the form
    if request.method == 'POST':
        # Cretes a form and adds the data from the form
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
            return redirect('home')
        else:
            form = UserForm()
            messages.error(request, "Invalid information")
            return render(request, 'register/register.html', {'form': form, 'error': 'Form is not valid'})
    else:
        form = UserForm()  # Instantiate an empty form for GET request
    return render(request, 'register/register.html', {'form': form})


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
            # If the user is authenticated, log the user in
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form = LoginForm()
                messages.error(request, "Invalid username or password")
                return render(request, 'register/login.html', {'form': form, 'error': 'Invalid username or password'})
        else:
            form = LoginForm()
            messages.error(request, "Invalid information")
            return render(request, 'register/login.html', {'form': form, 'error': 'Form is not valid'})
    else:
        form = LoginForm()
        return render(request, 'register/login.html', {'form': form})
