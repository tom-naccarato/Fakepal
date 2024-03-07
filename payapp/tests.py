from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from payapp.models import Account, Request


class PayAppViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a user and an admin user
        self.user = User.objects.create_user(username='user', password='userpassword')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword')
        self.admin_group = Group.objects.get(name='AdminGroup')  # Not created as created on model activation
        self.admin_user.groups.add(self.admin_group)
        # Create accounts for each user
        Account.objects.create(user=self.user, balance=100)
        Account.objects.create(user=self.admin_user, balance=100)
        # Log in the regular user by default
        self.client.login(username='user', password='userpassword')

    def test_transactions_view(self):
        # Test accessing the transactions page as a logged-in user
        response = self.client.get(reverse('payapp:transactions'))
        self.assertEqual(response.status_code, 200)

        # Test accessing the transactions page as a logged-out user
        self.client.logout()
        response = self.client.get(reverse('payapp:transactions'))
        self.assertNotEqual(response.status_code, 200)

    def test_make_request_view(self):
        # Test making a request as a logged-in user
        receiver = User.objects.create_user(username='receiver', password='receiverpassword')
        Account.objects.create(user=receiver, balance=50)
        response = self.client.post(reverse('payapp:make_request'), {
            'amount': 10,
            'receiver': receiver.username,
            'message': 'Test request',
        })
        # Check if the request is created
        self.assertTrue(Request.objects.filter(sender__user=self.user, receiver__user=receiver).exists())
        self.assertEqual(response.status_code, 302)  # Redirect to home indicates success

    def test_make_request_invalid_receiver(self):
        # Test for attempting to make a request to a non-existent user
        response = self.client.post(reverse('payapp:make_request'), {
            'amount': 10,
            'receiver': 'nonexistentuser',
        })
        self.assertEqual(response.status_code, 200)

    def test_accept_request_view(self):
        # Create a request to be accepted
        receiver = User.objects.create_user(username='receiver', password='receiverpassword')
        Account.objects.create(user=receiver, balance=50)
        req = Request.objects.create(sender=Account.objects.get(user=receiver),
                                     receiver=Account.objects.get(user=self.user), amount=10, status='pending')

        # Test accepting the request
        self.client.login(username='receiver', password='receiverpassword')
        response = self.client.get(reverse('payapp:accept_request', kwargs={'request_id': req.id}))
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(req.status, 'accepted')

    def test_accept_request_insufficient_funds(self):
        # Create a request to be accepted
        request_receiver = User.objects.create_user(username='receiver', password='receiverpassword')
        Account.objects.create(user=request_receiver, balance=5)
        req = Request.objects.create(sender=Account.objects.get(user=self.user),
                                     receiver=Account.objects.get(user=request_receiver), amount=10, status='pending')

        # Test accepting the request
        self.client.login(username='receiver', password='receiverpassword')
        response = self.client.get(reverse('payapp:accept_request', kwargs={'request_id': req.id}))
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(req.status, 'pending')

    def test_decline_request_view(self):
        # Create a request to be declined
        receiver = User.objects.create_user(username='declinereceiver', password='receiverpassword')
        Account.objects.create(user=receiver, balance=50)
        req = Request.objects.create(sender=Account.objects.get(user=receiver),
                                     receiver=Account.objects.get(user=self.user), amount=10, status='pending')

        # Test declining the request
        self.client.login(username='declinereceiver', password='receiverpassword')
        response = self.client.get(reverse('payapp:decline_request', kwargs={'request_id': req.id}))
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(req.status, 'declined')

    def test_cancel_request_view(self):
        # Create a request to be canceled
        sender = User.objects.create_user(username='canceluser', password='userpassword')
        Account.objects.create(user=sender, balance=50)
        req = Request.objects.create(sender=Account.objects.get(user=sender),
                                     receiver=Account.objects.get(user=self.user), amount=10, status='pending')

        # Test canceling the request
        self.client.login(username='canceluser', password='userpassword')
        response = self.client.get(reverse('payapp:cancel_request', kwargs={'request_id': req.id}))
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(req.status, 'cancelled')

    def test_send_payment_view(self):
        # Test sending a payment
        receiver = User.objects.create_user(username='paymentreceiver', password='receiverpassword')
        receiver_account = Account.objects.create(user=receiver, balance=50)
        sender_account = Account.objects.get(user=self.user)

        # Test sending the payment
        self.client.login(username='user', password='userpassword')
        response = self.client.post(reverse('payapp:send_payment'), {
            'amount': 10,
            'receiver': receiver.username,
            'message': 'Test payment',
        })
        sender_account.refresh_from_db()
        receiver_account.refresh_from_db()

        self.assertEqual(response.status_code, 302)  # Redirect to home indicates success
        self.assertEqual(sender_account.balance, 90)  # 100 - 10
        self.assertEqual(receiver_account.balance, 60)  # 50 + 10

    def test_send_payment_insufficient_funds(self):
        # Test for attempting to send a payment with insufficient funds
        receiver = User.objects.create_user(username='paymentreceiver', password='receiverpassword')
        receiver_account = Account.objects.create(user=receiver, balance=50)
        sender_account = Account.objects.get(user=self.user)

        # Test sending the payment
        self.client.login(username='user', password='userpassword')
        response = self.client.post(reverse('payapp:send_payment'), {
            'amount': 110,  # More than the sender's balance
            'receiver': receiver.username,
            'message': 'Test payment',
        })
        sender_account.refresh_from_db()
        receiver_account.refresh_from_db()

        self.assertEqual(response.status_code, 200)  # No redirect indicates failure
        self.assertEqual(sender_account.balance, 100)  # No change
        self.assertEqual(receiver_account.balance, 50)  # No change

    def test_send_payment_invalid_receiver(self):
        # Test for attempting to send a payment to a non-existent user
        response = self.client.post(reverse('payapp:send_payment'), {
            'amount': 10,
            'receiver': 'nonexistentuser',
        })
        self.assertEqual(response.status_code, 200)
