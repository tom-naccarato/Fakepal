from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from payapp.custom_exceptions import InsufficientBalanceException
from payapp.forms import RequestForm, PaymentForm
from payapp.models import Transaction, Account, Request
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

    # Retains the docstring and name of the original function
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


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


def home(request):
    return render(request, 'payapp/home.html')


@login_required_message
def transactions(request):
    """
    View function to display the transactions of the logged-in user with login required decorator

    :param request:
    :return:
    """
    transactions_list = Transaction.objects.filter(
        Q(sender__user=request.user) | Q(receiver__user=request.user)
    ).select_related('sender', 'receiver', 'sender__user', 'receiver__user')
    print(transactions_list)
    return render(request, 'payapp/transactions.html', {'transactions': transactions_list})


@admin_login_required_message
def admin_all_users(request):
    """
    Admin view function to display all users with admin required decorator
    :param request:
    :return:
    """
    users_list = Account.objects.all()
    return render(request, 'payapp/admin_all_users.html', {'users': users_list})


@admin_login_required_message
def admin_all_transactions(request):
    """
    Admin view function to display all transactions with admin required decorator
    :param request:
    :return:
    """
    transactions_list = Transaction.objects.all()
    return render(request, 'payapp/admin_all_transactions.html',
                  {'transactions': transactions_list})


@login_required_message
def requests(request):
    """
    View function to display the requests of the logged-in user

    :param request:
    :return:
    """
    # Select outgoing requests where the status is pending
    outgoing_request_list = Request.objects.filter(
        Q(sender__user=request.user, status='pending')
    ).select_related('sender', 'receiver', 'sender__user', 'receiver__user')
    # Select incoming requests where the status is pending
    incoming_request_list = Request.objects.filter(
        Q(receiver__user=request.user, status='pending')
    ).select_related('sender', 'receiver', 'sender__user', 'receiver__user')
    # Select completed requests where the status is not pending
    completed_request_list = Request.objects.filter(
        (Q(sender__user=request.user) & ~Q(status='pending')) |
        (Q(receiver__user=request.user) & ~Q(status='pending'))
    ).select_related('sender', 'receiver', 'sender__user', 'receiver__user')

    # Render the requests page with the context
    context = {'outgoing_requests': outgoing_request_list, 'incoming_requests': incoming_request_list,
               'completed_requests': completed_request_list}
    return render(request, 'payapp/requests.html', context)


@login_required_message
def make_request(request):
    """
    View function to handle the request of a new user

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = RequestForm(request.POST, user=request.user)
        if form.is_valid():
            request_instance = form.save(commit=False)  # Creates an instance of the form without saving it
            request_instance.sender = Account.objects.get(user=request.user)
            request_instance.receiver = Account.objects.get(id=request.POST['receiver'])
            request_instance.save()
            messages.success(request, "Request has been made")
            return redirect('home')
        else:
            messages.error(request, "Invalid information. Please try again.")
            return render(request, 'payapp/make_request.html', {'form': form})
    else:
        form = RequestForm(user=request.user)
    return render(request, 'payapp/make_request.html', {'form': form})


@login_required_message
def accept_request(request, request_id):
    """
    View function to accept a request from another user


    :param request:
    :param request_id: The id of the request object
    :return:
    """
    # Try to accept the request
    try:
        req = get_object_or_404(Request, id=request_id)
        req.accept_request(req.amount)
        messages.success(request, "Request has been accepted")
        return redirect('payapp:requests')

    # If the request does not exist, display an error message and redirect to the requests page
    except Http404:
        messages.error(request, "The requested item does not exist.")
        return redirect('payapp:requests')

    # If the user does not have enough balance to accept the request, display an error message and
    # redirect to the requests page
    except InsufficientBalanceException as e:
        messages.error(request, "You do not have enough balance to accept this request. "
                                "Please add funds to your account.")
        return redirect('payapp:requests')

    except ValueError as e:
        messages.error(request, "You cannot request a negative number. Please try again.")


@login_required_message
def decline_request(request, request_id):
    """
    View function to decline a request from another user

    :param request:
    :param request_id: The id of the request object
    :return:
    """
    # Try to decline the request
    try:
        req = get_object_or_404(Request, id=request_id)
        req.decline_request()
        messages.success(request, "Request has been declined")
        return redirect('payapp:requests')
    # If the request does not exist, display an error message and redirect to the requests page
    except Http404:
        messages.error(request, "Request does not exist. Please try again.")
        return redirect('payapp:requests')
    # If an error occurs, display an error message and redirect to the requests page
    except:
        messages.error(request, "An error occurred. Please try again.")
        return redirect('payapp:requests')

@login_required_message
def send_payment(request):
    """
    View function to send payment to another user

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                transaction_instance = form.save(commit=False)
                transaction_instance.sender = Account.objects.get(user=request.user)
                transaction_instance.receiver = Account.objects.get(id=request.POST['receiver'])
                transaction_instance.transfer(transaction_instance.amount)
                transaction_instance.save()
                messages.success(request, "Payment has been made")
                return redirect('home')
            except InsufficientBalanceException as e:
                messages.error(request, "You do not have enough balance to make this payment. "
                                        "Please add funds to your account.")
                return render(request, 'payapp/send_payment.html', {'form': form})
            except ValueError as e:
                messages.error(request, "You cannot transfer a negative number. Please try again.")
                return render(request, 'payapp/send_payment.html', {'form': form})
        else:
            messages.error(request, "Invalid information. Please try again.")
            return render(request, 'payapp/send_payment.html', {'form': form})
    else:
        form = RequestForm(user=request.user)
    return render(request, 'payapp/send_payment.html', {'form': form})
