from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect

from payapp.models import Transaction
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
    transactions_list = (Transaction.objects.filter(Q(sender__user=request.user) | Q(receiver__user=request.user))
                         .select_related('sender', 'receiver'))
    return render(request, 'payapp/transactions.html', {'transactions': transactions_list})
