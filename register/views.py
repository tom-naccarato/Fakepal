from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from register.forms import UserForm


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
        username = request.POST['username']
        password = request.POST['password']
        # Authenticates the user
        user = authenticate(request, username=username, password=password)
        # If the user is authenticated, log the user in
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'register/login.html')
