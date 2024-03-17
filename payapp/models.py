from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from payapp.custom_exceptions import InsufficientBalanceException
from payapp.utils import convert_currency
from django.db import transaction


class Account(models.Model):
    """
    Account model for storing user account information.

    Attributes:
    - user: OneToOneField to User model
    - balance: DecimalField to store account balance
    - CURRENCY_CHOICES: Tuple of tuples to store currency choices
    - currency: CharField to store currency type
    - created_at: DateTimeField to store account creation date
    - STATUS_CHOICES: Tuple of tuples to store account status choices
    - status: CharField to store account status

    Methods:
    - __str__: Returns the username of the user linked to the account
    - change_balance: Modifies the account balance by a specified amount
    """

    class Meta:
        db_table = 'account'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False, related_name='account')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    CURRENCY_CHOICES = (
        ('gbp', 'GBP'),
        ('usd', 'USD'),
        ('eur', 'EUR'),
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='gbp')
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        """
        Returns the username of the user linked to the account.

        :return: str: The username of the user linked to the account
        """
        return self.user.username


class Transfer(models.Model):
    """
    Transaction model for storing transaction information.

    Attributes:
    - sender: ForeignKey to Account model for the sender account
    - receiver: ForeignKey to Account model for the receiver account
    - amount: DecimalField to store transaction amount
    - created_at: DateTimeField to store transaction creation date
    - type: CharField to store transaction type (transfer or request)

    Methods:
    - __str__: Returns the transaction type and amount
    - transfer: Transfers the specified amount from the sender's account to the receiver's account
    """

    class Meta:
        db_table = 'transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    sender = models.ForeignKey(Account, on_delete=models.CASCADE,
                               related_name='transaction_sender')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE,
                                 related_name='transaction_receiver')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    TRANSACTION_TYPE_CHOICES = (
        ('request', 'Request'),
        ('transfer', 'Transfer'),
    )
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, default='transfer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the transaction type and amount.

        :return: str: The transaction type and amount
        """
        return f'{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}'

    @transaction.atomic
    def execute(self, amount):
        """
        Transfers the specified amount from the sender's account to the receiver's account.

        :param amount: The amount to transfer from the sender's account to the receiver's account

        :return: None
        """
        # Checks that the sender has enough balance to transfer the amount
        if self.sender.balance < amount:
            raise InsufficientBalanceException
        # Ensures that the amount to transfer is positive so users cannot transfer negative/zero amounts
        if self.amount <= 0:
            raise ValueError

        # If the transaction type is a transfer, the amount is subtracted from the sender's balance, convert
        # and add to the receiver's balance
        if self.type == 'transfer':
            self.sender.balance -= amount
            converted_amount = convert_currency(self.sender.currency, self.receiver.currency, amount)
            self.receiver.balance += converted_amount

        # If the transaction type is a request, the amount is converted first and then transferred
        else:
            converted_amount = convert_currency(self.receiver.currency, self.sender.currency, amount)
            self.sender.balance -= converted_amount
            self.receiver.balance += amount
            self.amount = converted_amount

        # Save the sender, receiver and transfer
        self.sender.save()
        self.receiver.save()
        self.save()
        return None


class Request(models.Model):
    """
    Request model for storing request information.

    Attributes:
    - sender: ForeignKey to Account model for the sender account
    - receiver: ForeignKey to Account model for the receiver account
    - amount: DecimalField to store request amount
    - created_at: DateTimeField to store request creation date
    - REQUEST_STATUS_CHOICES: Tuple of tuples to store request status choices
    - status: CharField to store request status

    Methods:
    - __str__: Returns the request type and amount
    - accept_request: Accepts a request, creates and executes a transaction and sets req. to accepted
    - decline_request: Declines a request and sets req. to declined
    """

    class Meta:
        db_table = 'request'
        verbose_name = 'Request'
        verbose_name_plural = 'Requests'

    sender = models.ForeignKey(Account, on_delete=models.CASCADE,
                               related_name='request_sender')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE,
                                 related_name='request_receiver')
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                 default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    REQUEST_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled')
    )
    status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default='pending')

    def __str__(self):
        """
        Returns the request type and amount.

        :return: str: The request type and amount
        """
        return f'{self.sender.user.username} requested {self.amount} from {self.receiver.user.username}'

    def accept_request(self, amount):
        """
        Accepts a request, creates and executes a transaction and sets req. to accepted.

        :param amount:

        :return:
        """

        # Checks that the receiver of the request has enough balance to accept the request
        if self.receiver.balance >= amount:
            with transaction.atomic():
                # Creates a transaction
                transfer = Transfer(sender=self.receiver, receiver=self.sender,
                                    amount=amount, type='request')
                transfer.save()
                # Executes the transaction
                transfer.execute(amount)
                self.status = 'accepted'
                self.save()
                return None
        # If the receiver does not have enough balance to accept the request, raise an exception
        else:
            raise InsufficientBalanceException

    @transaction.atomic
    def decline_request(self):
        """
        Declines a request and sets req.

        :return: None
        """
        self.status = 'declined'
        self.save()
        return None

    @transaction.atomic
    def cancel_request(self):
        """
        Cancels a request and sets req.

        :return: None
        """
        self.status = 'cancelled'
        self.save()
        return None


class Notification(models.Model):
    """
    Notification model for storing notification information.

    Attributes:
    - from_user: ForeignKey to User model for the user
    - to_user: ForeignKey to User model for the user
    - NOTIFICATION_TYPE_CHOICES: Tuple of tuples to store notification type choices
    - notification_type: IntegerField to store notification type
    - message: CharField to store notification message
    - created_at: DateTimeField to store notification creation date
    - read: BooleanField to store whether the notification has been read

    Methods:
    - __str__: Returns the notification message
    - mark_as_read: Marks the notification as read
    """

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    from_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_notification')
    to_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_notification')
    NOTIFICATION_TYPE_CHOICES = (
        ('payment_sent', 'Payment Sent'),
        ('request_sent', 'Request Sent'),
        ('request_accepted', 'Request Accepted'),
        ('request_declined', 'Request Declined'),
    )

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='payment_sent')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the notification message.

        :return: str: The notification message
        """
        return self.message

    @transaction.atomic
    def mark_as_read(self):
        """
        Marks the notification as read.

        :return: None
        """
        self.read = True
        self.save()
        return None
