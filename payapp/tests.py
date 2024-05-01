from threading import Thread
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from payapp.models import Account, Request, Notification
from thrift_timestamp import server


class PayAppViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Stop the Thrift server
        server.stop_thrift_server()
        print('Thrift server stopped.')

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

    def test_transfers_view(self):
        # Test accessing the transactions page as a logged-in user
        response = self.client.get(reverse('payapp:transfers'))
        self.assertEqual(response.status_code, 200)

        # Test accessing the transactions page as a logged-out user
        self.client.logout()
        response = self.client.get(reverse('payapp:transfers'))
        self.assertNotEqual(response.status_code, 200)

    def test_make_request_view(self):
        """
        Test making a request as a logged-in user and ensure a notification is created.
        """
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

        # Verify that a notification has been created for the receiver
        self.assertTrue(Notification.objects.filter(to_user__user=receiver, from_user__user=self.user,
                                                    notification_type='request_sent').exists())

    def test_make_request_invalid_receiver(self):
        # Test for attempting to make a request to a non-existent user
        response = self.client.post(reverse('payapp:make_request'), {
            'amount': 10,
            'receiver': 'nonexistentuser',
        })
        self.assertEqual(response.status_code, 200)  # No redirect indicates failure

    def test_accept_request_view(self):
        """
        Test accepting a request and ensure a notification is created for the sender and that
        the corresponding 'request_sent' notification is marked as read.
        """
        # Create a request to be accepted
        receiver = User.objects.create_user(username='receiver', password='receiverpassword')
        receiver_account = Account.objects.create(user=receiver, balance=50)
        sender_account = Account.objects.get(user=self.user)
        req = Request.objects.create(sender=receiver_account, receiver=sender_account, amount=10, status='pending')

        # Manually create a notification for the request being sent
        Notification.objects.create(from_user=receiver_account, to_user=sender_account, request=req,
                                    notification_type='request_sent', message='Test notification')

        # Verify that the 'request_sent' notification exists before accepting the request
        self.assertTrue(Notification.objects.filter(request=req, notification_type='request_sent').exists())

        # Test accepting the request
        self.client.login(username='receiver', password='receiverpassword')
        response = self.client.get(reverse('payapp:accept_request', kwargs={'request_id': req.id}))
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(req.status, 'accepted')  # The request is accepted successfully

        # Verify that a notification has been created for the sender indicating the request was accepted
        self.assertTrue(Notification.objects.filter(to_user=receiver_account, from_user=sender_account,
                                                    notification_type='request_accepted').exists())

        # Also, check that the 'request_sent' notification is now marked as read
        request_sent_notification = Notification.objects.get(request=req, notification_type='request_sent')
        self.assertTrue(request_sent_notification.read)

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
        self.assertEqual(req.status, 'pending')  # The request is not accepted due to insufficient funds

    def test_decline_request_view(self):
        """
        Test declining a request and ensure a notification is created for the sender.
        """
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
        self.assertEqual(req.status, 'declined')  # The request is declined successfully

        # Verify that a notification has been created for the sender
        self.assertTrue(Notification.objects.filter(to_user=req.sender, from_user=req.receiver,
                                                    notification_type='request_declined').exists())

    def test_cancel_request_view(self):
        """
        Test canceling a request and ensure a notification is created for the receiver.
        """
        # Create a request to be canceled
        sender = User.objects.create_user(username='canceluser', password='userpassword')
        Account.objects.create(user=sender, balance=50)
        req = Request.objects.create(sender=Account.objects.get(user=sender),
                                     receiver=Account.objects.get(user=self.user), amount=10, status='pending')

        # Test canceling the request
        self.client.login(username='canceluser', password='userpassword')
        response = self.client.get(reverse('payapp:cancel_request', kwargs={'request_id': req.id}))
        req.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Redirect to home indicates success
        self.assertEqual(req.status, 'cancelled')  # The request is cancelled successfully

        # Verify that a notification has been created for the receiver
        self.assertTrue(Notification.objects.filter(to_user=req.receiver, from_user=req.sender,
                                                    notification_type='request_cancelled').exists())

    def test_send_payment_view(self):
        """
        Test sending a payment and ensure a notification is created for the receiver.
        """
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

        # Verify that a notification has been created for the receiver
        self.assertTrue(Notification.objects.filter(to_user=receiver_account, from_user=sender_account,
                                                    notification_type='payment_sent').exists())

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
