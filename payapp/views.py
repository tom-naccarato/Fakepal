from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from payapp.custom_exceptions import InsufficientBalanceException
from payapp.forms import RequestForm, PaymentForm
from payapp.models import Transfer, Account, Request, Notification
from webapps2024 import settings
from django.db import transaction

currency_symbols = {
    'USD': '$',
    'GBP': '£',
    'EUR': '€'
}


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


def home(request):
    """
    View function to display the home page
    :param request:
    :return:
    """
    return render(request, 'payapp/home.html')


@login_required_message
def transfers(request):
    """
    View function to display the transfers of the logged-in user with login required decorator

    :param request:
    :return:
    """
    transfer_list = (Transfer.objects.filter(
        Q(sender__user=request.user) | Q(receiver__user=request.user)
    ))
    if transfer_list.exists():
        transfer_list = transfer_list.select_related('sender', 'receiver', 'sender__user',
                                                     'receiver__user').order_by('-created_at')
    return render(request, 'payapp/transfers.html', {'transfers': transfer_list})


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
    user = request.user
    account = Account.objects.get(user=user)
    # If the form is submitted, validate the form and save the request
    if request.method == 'POST':
        form = RequestForm(request.POST, user_currency=account.currency)  # Passes currency for constructor
        # If the form is valid, save the request
        if form.is_valid():
            try:
                # Checks if the amount is positive, if not, display an error message and return the form
                if form.cleaned_data.get('amount') <= 0:
                    messages.error(request, "You must request a positive sum. Please try again.")
                    return render(request, 'payapp/make_request.html', {'form': form})

                with transaction.atomic():  # Ensures that the request is saved in the same transaction as the sender
                    # and receiver accounts to maintain atomicity
                    request_instance = form.save(commit=False)  # Creates an instance of the form without saving it
                    request_instance.sender = Account.objects.get(user=request.user)
                    request_instance.receiver = Account.objects.get(user__username=request.POST['receiver'])

                    # If the receiver is not the sender, save the request
                    if request_instance.receiver != request_instance.sender:
                        request_instance.save()
                        notification = Notification.objects.create(
                            to_user=request_instance.receiver,
                            from_user=request_instance.sender,
                            message=f"{request_instance.sender.user.username} has requested "
                                    f"{currency_symbols.get(request_instance.sender.currency.upper())}"
                                    f"{request_instance.amount}",
                            notification_type='request_sent',
                            created_at=request_instance.created_at,
                            request=request_instance
                        )
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
        form = RequestForm(user_currency=account.currency)
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
    with transaction.atomic():
        try:
            req = get_object_or_404(Request, id=request_id)
            req.accept_request(req.amount)
            # Adds a notification to the sender's account
            notification = Notification.objects.create(
                to_user=req.sender,
                from_user=req.receiver,
                message=f"Your request for {currency_symbols.get(req.sender.currency.upper())}{req.amount} from "
                        f"{req.receiver.user.username} has been accepted.",
                notification_type='request_accepted',
                created_at=req.created_at,
                request=req
            )
            notification.save()
            # Marks the request sent notification as read
            request_notification = Notification.objects.get(request=req, notification_type='request_sent')
            request_notification.read = True
            request_notification.save()
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
    # Try to decline the request in an atomic transaction
    with transaction.atomic():
        try:
            req = get_object_or_404(Request, id=request_id)
            req.decline_request()
            # Adds a notification to the sender's account
            notification = Notification.objects.create(
                to_user=req.sender,
                from_user=req.receiver,
                message=f"Your request for {currency_symbols.get(req.sender.currency.upper())}{req.amount} from "
                        f"{req.receiver.user.username} has been declined.",
                notification_type='request_declined',
                created_at=req.created_at,
                request=req
            )
            notification.save()
            messages.success(request, "Request has been declined.")
            # Marks the request sent notification as read
            request_notification = Notification.objects.get(request=req, notification_type='request_sent')
            request_notification.read = True
            request_notification.save()
            return redirect('payapp:requests')
        # If the request does not exist, display an error message and redirect to the requests page
        except Http404:
            messages.error(request, "Request does not exist. Please try again.")
            return redirect('payapp:requests')
        # If any other error occurs, display an error message and redirect to the requests page
        except:
            messages.error(request, "An error occurred. Please try again.")
            return redirect('payapp:requests')


@transaction.atomic
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
        # Adds a notification to the receiver's account
        notification = Notification.objects.create(
            to_user=req.receiver,
            from_user=req.sender,
            message=f"{req.sender.user.username} has cancelled their request for "
                    f"{currency_symbols.get(req.sender.currency.upper())}{req.amount}",
            notification_type='request_cancelled',
            created_at=req.created_at,
            request=req,
        )
        notification.save()
        print(notification)
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
    user = request.user
    account = Account.objects.get(user=user)
    # If the form is submitted, validate the form and save the payment
    if request.method == 'POST':
        form = PaymentForm(request.POST, user_currency=account.currency)
        # If the form is valid, save the payment
        if form.is_valid():
            # Try to save the payment
            with transaction.atomic():
                try:
                    transaction_instance = form.save(commit=False)
                    transaction_instance.sender = Account.objects.get(user=request.user)
                    transaction_instance.receiver = Account.objects.get(user__username=request.POST['receiver'])
                    # Makes sure the sender is not the receiver
                    if transaction_instance.receiver != transaction_instance.sender:
                        transaction_instance.execute(transaction_instance.amount)
                        transaction_instance.save()
                        # Adds a notification to the receiver's account
                        notification = Notification.objects.create(
                            to_user=transaction_instance.receiver,
                            from_user=transaction_instance.sender,
                            message=f"You have received {currency_symbols.get(account.currency.upper())}"
                                    f"{transaction_instance.amount} from "
                                    f"{transaction_instance.sender.user.username}",
                            notification_type='payment_sent',
                            created_at=transaction_instance.created_at
                        )
                        notification.save()

                        messages.success(request, "Payment has been made")
                        return redirect('home')
                    else:
                        messages.error(request, "You cannot send money to yourself! Please try again.")
                        return render(request, 'payapp/send_payment.html', {'form': form})

                # If the user does not have enough balance to make the payment, display an error message and return
                # the form
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
                    messages.error(request, "The user does not exist. Please make sure you spelled" +
                                   "their username correctly and try again.")
                    return render(request, 'payapp/send_payment.html', {'form': form})

        # If the form is invalid, display an error message and return the form
        else:
            messages.error(request, "Invalid information. Please try again.")
            return render(request, 'payapp/send_payment.html', {'form': form})

    # If the form is not submitted, display the form
    else:
        form = PaymentForm(user_currency=account.currency)
        return render(request, 'payapp/send_payment.html', {'form': form})


@login_required_message
def notifications(request):
    """
    View function to display the notifications of the logged-in user

    :param request:
    :return:
    """
    user = request.user
    account = Account.objects.get(user=user)
    # Select notifications where the receiver is the logged-in user
    notifications_list = (Notification.objects.filter(to_user=account, read=False))
    if notifications_list.exists():
        notifications_list = notifications_list.order_by('-created_at')
    # Render the notifications page with the context
    return render(request, 'payapp/notifications.html', {'notifications': notifications_list})

@login_required_message
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, to_user=request.user.account)
        notification.read = True
        notification.save()
        # Redirect to the appropriate page based on the notification type
        if notification.notification_type == 'payment_sent':
            return redirect('payapp:transfers')
        else:
            return redirect('payapp:requests')
    except Notification.DoesNotExist:
        # Handle the case where the notification doesn't exist
        messages.error(request, "Notification not found.")
        return redirect('home')  # Redirect to a safe page
