from django.shortcuts import get_object_or_404

from payapp.models import Account, Notification


def get_unread_notifications(request):
    """
    This function returns the number of incoming transactions for the logged-in user
    :param request: HttpRequest object
    :return: Dictionary containing the count of incoming requests
    """
    incoming_count = None  # Default value

    if request.user.is_authenticated:
        user_account = get_object_or_404(Account, user=request.user)
        incoming_count = Notification.objects.filter(to_user=user_account, read=False).count()
        return {'unread_notifications_count': incoming_count}
    else:
        return {'unread_notifications_count': None}

def user_currency(request):
    """
    This function returns the currency of the logged-in user
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        user_account = get_object_or_404(Account, user=request.user)
        currency = user_account.currency
        return {'user_currency': currency}
    else:
        return {'user_currency': None}

def user_balance(request):
    """
    This function returns the balance of the logged-in user
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        user_account = get_object_or_404(Account, user=request.user)
        balance = user_account.balance
        return {'user_balance': balance}
    else:
        return {'user_balance': None}
