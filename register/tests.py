from threading import Thread
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from register.forms import UserForm, LoginForm
from payapp.utils import convert_currency
from thrift_timestamp import server


class UserViewTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Stop the Thrift server
        server.stop_thrift_server()
        print('Thrift server stopped.')

    def setUp(self):
        self.client = Client()
        # self.admin_group = Group.objects.create(name='AdminGroup')
        User.objects.create_user(username='testuser1', first_name='Test', last_name='User', password='testpassword123',
                                 email='test@example.com')

    @patch('register.forms.convert_currency')
    def test_register_view_post_success(self, mock_convert):
        mock_convert.return_value = 1000
        # Test successful registration
        response = self.client.post(reverse('register:register'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'new@example.com',
            'currency': 'gbp'
        })
        mock_convert.return_value = 1000
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(self.client.login(username='newuser', password='newpassword123'))

    @patch('register.forms.convert_currency')  # Mock the convert_currency function to return a fixed value
    def test_register_view_post_invalid(self, mock_convert):
        mock_convert.return_value = 1000
        # Test registration with invalid data
        response = self.client.post(reverse('register:register'), {
            'username': 'user',
            'password1': 'pwd1',
            'password2': 'pwd2',  # Mismatching passwords
            'email': 'user@example.com',
            'currency': 'gbp'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='user').exists())

    def test_register_view_get(self):
        # Test GET request returns an empty form
        response = self.client.get(reverse('register:register'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertFalse(response.context['form'].is_bound)

    def test_login_view_post_success(self):
        # Test successful login
        response = self.client.post(reverse('register:login'), {
            'username': 'testuser1',
            'password': 'testpassword123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_view_post_invalid(self):
        # Test login with invalid credentials
        response = self.client.post(reverse('register:login'), {
            'username': 'testuser1',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_view_get(self):
        # Test GET request returns a login form
        response = self.client.get(reverse('register:login'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], LoginForm)
