from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings

from payapp.custom_exceptions import CurrencyConversionError
from payapp.models import Account, Transfer, Request
from register.forms import UserForm


def admin_login_required_message(function):
    """
    Decorator to display a message if the user is not logged in
    """

    def wrap(request, *args, **kwargs):
        user = request.user

        # If the user is logged in and an admin, call the function
        if user.is_authenticated:
            if user.groups.filter(name="AdminGroup").exists():
                return function(request, *args, **kwargs)
            else:
                messages.error(request, "You need to be an admin to view this page.")
                return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        # If the user is not logged in, display an error message and redirect to the login page
        else:
            messages.error(request, "You need to be logged in to view this page.")
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    # Retains the docstring and name of the original function
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

@admin_login_required_message
def all_users(request):
    """
    Admin view function to display all users with admin required decorator
    :param request:
    :return:
    """
    users_list = Account.objects.filter(Q(user__groups=None)).select_related('user')
    admin_list = Account.objects.filter(Q(user__groups__name="AdminGroup")).select_related('user')
    context = {'users': users_list, 'admins': admin_list}
    return render(request, 'custom_admin/all_users.html', context)


@admin_login_required_message
def all_transactions(request):
    """
    Admin view function to display all transactions with admin required decorator
    :param request:
    :return:
    """
    transfer_list = Transfer.objects.all().order_by('-created_at')
    request_list = Request.objects.all().order_by('-created_at')

    return render(request, 'custom_admin/all_transactions.html',
                  {'transfers': transfer_list, 'requests': request_list})


@admin_login_required_message
def register(request):
    """
    Admin view function to register a new admin with admin required decorator
    :param request:
    :return:
    """
    if request.method == 'POST':
        # Declares a form and adds the data from the form
        form = UserForm(request.POST)
        # Checks if the form is valid
        if form.is_valid():
            # Tries to save the form, if it fails, an error message is displayed
            try:
                form.save()  # This will save the User and create an Account
            except CurrencyConversionError as e:
                messages.error(request, "A currency conversion error occurred. Please try again.")
                print(e)
                context = {'form': form, 'admin': True}
                return render(request, 'register/register.html', context)
            # Add the admin to the admin group
            admin = User.objects.get(username=form.cleaned_data.get('username'))
            admin_group = Group.objects.get(name='AdminGroup')
            admin.groups.add(admin_group)
            # Redirects the user to the home page after registration
            messages.success(request, f"Admin {admin} has been registered.")
            return redirect('home')
        else:
            messages.error(request, "Invalid information")
            context = {'form': form, 'admin': True}
            return render(request, 'register/register.html', context)
    else:
        form = UserForm()
        context = {'form': form, 'admin': True}
    return render(request, 'register/register.html', context)
