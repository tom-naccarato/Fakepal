from django.contrib.auth.models import User
from django.db import models
from payapp.custom_exceptions import InsufficientBalanceException
from django.contrib import messages


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
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='gdp')
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

    def change_balance(self, amount):
        """
    Modifies the account balance by a specified amount. The amount can be positive (for deposits)
    or negative (for withdrawals).

    :param amount: The amount to adjust the balance by. Can be positive or negative.
    :type amount: Decimal

    :return: The updated account balance after applying the change.
    :rtype: Decimal
    """
        self.balance += amount
        self.save()
        return self.balance


class Transaction(models.Model):
    """
    Transaction model for storing transaction information.

    Attributes:
    - sender: ForeignKey to Account model for the sender account
    - receiver: ForeignKey to Account model for the receiver account
    - amount: DecimalField to store transaction amount
    - created_at: DateTimeField to store transaction creation date

    Methods:
    - __str__: Returns the transaction type and amount
    - transfer: Transfers the specified amount from the sender's account to the receiver's account
    """

    class Meta:
        db_table = 'transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    sender = models.ForeignKey(Account, on_delete=models.CASCADE,
                               related_name='sent_transactions')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE,
                                 related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the transaction type and amount.

        :return: str: The transaction type and amount
        """
        return f'{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}'

    def transfer(self, amount):
        """
        Transfers the specified amount from the sender's account to the receiver's account.

        :param amount: The amount to transfer from the sender's account to the receiver's account
        :type amount: Decimal

        :return: None
        """
        if self.sender.balance < amount:
            raise InsufficientBalanceException
        # Ensures that the amount to transfer is positive so users cannot transfer negative amounts
        if self.amount <= 0:
            raise ValueError
        self.sender.balance -= amount
        self.receiver.balance += amount
        self.sender.save()
        self.receiver.save()
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
                               related_name='sent_requests')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE,
                                 related_name='received_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                 default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    REQUEST_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
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
            # Creates a transaction
            transaction = Transaction(sender=self.receiver, receiver=self.sender,
                                      amount=amount)
            transaction.save()
            # Executes the transaction
            transaction.transfer(amount)
            self.status = 'accepted'
            self.save()
            return None
        # If the receiver does not have enough balance to accept the request, raise an exception
        else:
            raise InsufficientBalanceException

    def decline_request(self):
        """
        Declines a request and sets req.

        :return: None
        """
        self.status = 'declined'
        self.save()
        return None
