from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect

from payapp.models import Transaction, Account
from webapps2024 import settings


def login_required_message(function):
    """
    Decorator to display a message if the user is not logged in
    """

    def wrap(request, *args, **kwargs):
        # If the user is logged in, call the function
        if request.user.is_authenticated:
            return function(request, *args, **kwargs)
        # If the user is not logged in, display an error message and redirect to the login page
        else:
            messages.error(request, "You need to be logged in to view this page.")
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def home(request):
    return render(request, 'payapp/home.html')


@login_required_message
def transactions(request):
    """
    View function to display the transactions of the logged-in user

    :param request:
    :return:
    """
    # Create a test transaction to see if the query works
    transactions_list = Transaction.objects.filter(
        Q(sender__user=request.user) | Q(receiver__user=request.user)
    ).select_related('sender', 'receiver', 'sender__user', 'receiver__user')
    print(transactions_list)
    return render(request, 'payapp/transactions.html', {'transactions': transactions_list})

def admin_all_users(request):
    """
    View function to display all users
    :param request:
    :return:
    """
    user = request.user
    if user.is_authenticated:
        if user.groups.filter(name="AdminGroup").exists():
            users_list = Account.objects.all()
            return render(request, 'payapp/admin_all_users.html', {'users': users_list})
        else:
            messages.error(request, "You need to be an admin to view this page.")
            return redirect('home')
    else:
        messages.error(request, "You need to be logged in and admin to view this page.")
        return redirect('home')
