from threading import Thread
from unittest.mock import patch
from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse
from payapp.models import Account
from register.forms import UserForm
from timestamp_server import thrift_server


class CustomAdminViewTests(TestCase):
    # Stops the Thrift server after all tests have run
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Stop the Thrift server
        thrift_server.stop_thrift_server()
        print("Thrift server stopped")

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

    def test_admin_all_users_view(self):
        """
        Test the admin all users view with a successful GET request
        :param self:
        :return:
        """
        # Test accessing the admin users page as an admin
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('custom_admin:all_users'))
        self.assertEqual(response.status_code, 200)

        # Test accessing the admin users page as a non-admin
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('custom_admin:all_users'))
        self.assertNotEqual(response.status_code, 200)

    @patch('register.forms.convert_currency')
    def test_admin_register_view_post_success(self, mock_convert):
        mock_convert.return_value = 1000
        """
        Test the admin register view with a successful POST request
        :param self:
        :return:
        """
        # Test successful admin registration
        self.client.login(username='admin1', password='admin1')
        response = self.client.post(reverse('custom_admin:register'), {
            'username': 'adminuser1',
            'first_name': 'Admin',
            'last_name': 'User',
            'password1': 'adminpassword123',
            'password2': 'adminpassword123',
            'email': 'admin@example.com',
            'currency': 'gbp'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        new_admin = User.objects.get(username='adminuser')
        self.assertTrue(new_admin.groups.filter(name='AdminGroup').exists())

    @patch('register.forms.convert_currency')
    def test_admin_register_view_post_invalid(self, mock_convert):
        mock_convert.return_value = 1000
        """
        Test the admin register view with an invalid POST request
        :param self:
        :return:
        """
        # Test registration with invalid data
        self.client.login(username='admin1', password='admin1')
        response = self.client.post(reverse('custom_admin:register'), {
            'username': 'adminuser1',
            'password1': 'pwd1',
            'password2': 'pwd2',  # Mismatching passwords
            'email': 'admin@email.com',
            'currency': 'gbp'
})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='adminuser1').exists())

    def test_admin_register_view_get(self):
        """
        Test the admin register view with a GET request
        :param self:
        :return:
        """
        # Test GET request returns an empty form
        self.client.login(username='admin1', password='admin1')
        response = self.client.get(reverse('custom_admin:register'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertFalse(response.context['form'].is_bound)

    def test_admin_all_transactions_view(self):
        """
        Test the admin all transactions view with a successful GET request
        :param self:
        :return:
        """
        # Test accessing the admin transactions page as an admin
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('custom_admin:all_transactions'))
        self.assertEqual(response.status_code, 200)

        # Test accessing the admin transactions page as a non-admin
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('custom_admin:all_transactions'))
        self.assertNotEqual(response.status_code, 200)

    def test_admin_login_required_message_decorator(self):
        """
        Test the admin login required message decorator
        :param self:
        :return:
        """
        # Test accessing the admin transactions page as an admin
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('custom_admin:all_transactions'))
        self.assertEqual(response.status_code, 200)

        # Test accessing the admin transactions page as a non-admin
        self.client.login(username='user', password='userpassword')
        response = self.client.get(reverse('custom_admin:all_transactions'))
        self.assertNotEqual(response.status_code, 200)

        # Test accessing the admin users page as an admin
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('custom_admin:all_users'))
        self.assertEqual(response.status_code, 200)


