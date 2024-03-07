from django.shortcuts import get_object_or_404

from payapp.models import Request, Account



def incoming_requests_count(request):
    """
    This function returns the number of incoming transactions for the logged-in user
    :param request: HttpRequest object
    :return: Dictionary containing the count of incoming requests
    """
    incoming_count = None  # Default value

    if request.user.is_authenticated:
        user_account = get_object_or_404(Account, user=request.user)
        incoming_count = Request.objects.filter(receiver=user_account, status='pending').count()
        return {'incoming_requests_count': incoming_count}
    else:
        return {'incoming_requests_count': None}

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
