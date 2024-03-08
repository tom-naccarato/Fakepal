from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from payapp.custom_exceptions import InsufficientBalanceException
from payapp.forms import RequestForm, PaymentForm
from payapp.models import Transaction, Account, Request
from webapps2024 import settings
import requests


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
def convert_currency(currency1, currency2, amount_of_currency1):
    # If the currencies are the same, return the amount of currency1
    if currency1 == currency2:
        return amount_of_currency1
    try:
        response = requests.get(f'http://localhost:8000/webapps2024/conversion/{currency1.upper()}/{currency2.upper()}/'
                                f'{amount_of_currency1}')
    except Exception:
        raise Exception('Error in currency conversion, please try again')
    # If the request is unsuccessful, raise an exception
    if response.status_code != 200:
        raise Exception('Error in currency conversion, please try again')

    # If the request is successful, returns the result, which is the amount of currency1 converted to currency2
    converted_amount = Decimal(response.content)
    return converted_amount

def home(request):
    """
    View function to display the home page
    :param request:
    :return:
    """
    return render(request, 'payapp/home.html')


@login_required_message
def transactions(request):
    """
    View function to display the transactions of the logged-in user with login required decorator

    :param request:
    :return:
    """
    transactions_list = (Transaction.objects.filter(
        Q(sender__user=request.user) | Q(receiver__user=request.user)
    ))
    if transactions_list.exists():
        transactions_list = transactions_list.select_related('sender', 'receiver', 'sender__user',
                                                             'receiver__user').order_by('-created_at')
    return render(request, 'payapp/transactions.html', {'transactions': transactions_list})


@login_required_message
def payment_requests(request):
    """
    View function to display the requests of the logged-in user

    :param request:
    :return:
    """
    # Select outgoing requests where the status is pending
    outgoing_request_list = (Request.objects.filter(
        Q(sender__user=request.user, status='pending')
    ))
    # Checks that the outgoing request list is not empty as cannot select_related on an empty queryset
    if outgoing_request_list.exists():
        outgoing_request_list = (outgoing_request_list.select_related('sender', 'receiver', 'sender__user',
                                                                      'receiver__user')
                                 .order_by('-created_at'))
    # Select incoming requests where the status is pending
    incoming_request_list = Request.objects.filter(
        Q(receiver__user=request.user, status='pending')
    )
    if incoming_request_list.exists():
        (incoming_request_list.select_related('sender', 'receiver', 'sender__user', 'receiver__user')
         .order_by('-created_at'))
    # Select completed requests from transaction table where the sender or receiver is the logged-in user

    completed_request_list = (Request.objects.filter(
        (Q(sender__user=request.user) & ~Q(status='pending')) |
        (Q(receiver__user=request.user) & ~Q(status='pending'))
    ))
    if completed_request_list.exists():
        completed_request_list = completed_request_list.select_related('sender', 'receiver', 'sender__user',
                                                                       'receiver__user').order_by('-created_at')

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
    # If the form is submitted, validate the form and save the request
    if request.method == 'POST':
        form = RequestForm(request.POST)
        # If the form is valid, save the request
        if form.is_valid():
            try:
                # Checks if the amount is positive, if not, display an error message and return the form
                if form.cleaned_data.get('amount') <= 0:
                    messages.error(request, "You must request a positive sum. Please try again.")
                    return render(request, 'payapp/make_request.html', {'form': form})
                request_instance = form.save(commit=False)  # Creates an instance of the form without saving it
                request_instance.sender = Account.objects.get(user=request.user)
                request_instance.receiver = Account.objects.get(user__username=request.POST['receiver'])

                # If the receiver is not the sender, save the request
                if request_instance.receiver != request_instance.sender:
                    request_instance.save()
                    messages.success(request, "Request has been made")

                # If the receiver is the sender, display an error message and return the form
                else:
                    messages.error(request, "You cannot request money from yourself! Please try again.")
                    return render(request, 'payapp/make_request.html', {'form': form})
                return redirect('home')
            # If the user does not exist, display an error message and return the form
            except User.DoesNotExist as e:
                messages.error(request, "The user does not exist. Please make sure you spelled their username"
                                        " correctly and try again.")
                return render(request, 'payapp/make_request.html', {'form': form})

        # If the form is invalid, display an error message and return the form
        else:
            messages.error(request, "Invalid information. Please try again.")
            return render(request, 'payapp/make_request.html', {'form': form})
    # If the form is not submitted, display the form
    else:
        form = RequestForm()
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

    # If the user tries to accept a negative number, display an error message and redirect to the requests page
    except ValueError as e:
        messages.error(request, "You cannot request a negative number. Please try again.")
        return redirect('payapp:requests')


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
        messages.success(request, "Request has been declined.")
        return redirect('payapp:requests')
    # If the request does not exist, display an error message and redirect to the requests page
    except Http404:
        messages.error(request, "Request does not exist. Please try again.")
        return redirect('payapp:requests')
    # If any other error occurs, display an error message and redirect to the requests page
    except:
        messages.error(request, "An error occurred. Please try again.")
        return redirect('payapp:requests')


def cancel_request(request, request_id):
    """
    View function to cancel a request to another user

    :param request:
    :param request_id: The id of the request object
    :return:
    """
    # Try to cancel the request
    try:
        req = get_object_or_404(Request, id=request_id)
        req.cancel_request()
        messages.success(request, "Request has been cancelled")
        return redirect('payapp:requests')
    # If the request does not exist, display an error message and redirect to the requests page
    except Http404:
        messages.error(request, "Request does not exist. Please try again.")
        return redirect('payapp:requests')
    # If an any other error occurs, display an error message and redirect to the requests page
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
    # If the form is submitted, validate the form and save the payment
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        # If the form is valid, save the payment
        if form.is_valid():
            # Try to save the payment
            try:
                transaction_instance = form.save(commit=False)
                transaction_instance.sender = Account.objects.get(user=request.user)
                transaction_instance.receiver = Account.objects.get(user__username=request.POST['receiver'])
                if transaction_instance.receiver != transaction_instance.sender:
                    transaction_instance.transfer(transaction_instance.amount)
                    transaction_instance.save()
                    messages.success(request, "Payment has been made")
                    return redirect('home')
                else:
                    messages.error(request, "You cannot send money to yourself! Please try again.")
                    return render(request, 'payapp/send_payment.html', {'form': form})
            # If the user does not have enough balance to make the payment, display an error message and return the form
            except InsufficientBalanceException as e:
                messages.error(request, "You do not have enough balance to make this payment. "
                                        "Please add funds to your account.")
                return render(request, 'payapp/send_payment.html', {'form': form})
            # If the user tries to transfer a negative number, display an error message and return the form
            except ValueError as e:
                messages.error(request, "You cannot transfer a negative number. Please try again.")
                return render(request, 'payapp/send_payment.html', {'form': form})
            # If the user does not exist, display an error message and return the form
            except User.DoesNotExist as e:
                messages.error(request, "The user does not exist. Please make sure you spelled their username"
                                        " correctly and try again.")
                return render(request, 'payapp/send_payment.html', {'form': form})

        # If the form is invalid, display an error message and return the form
        else:
            messages.error(request, "Invalid information. Please try again.")
            return render(request, 'payapp/send_payment.html', {'form': form})

    # If the form is not submitted, display the form
    else:
        form = PaymentForm()
        return render(request, 'payapp/send_payment.html', {'form': form})
