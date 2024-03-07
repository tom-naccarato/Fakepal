from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from register.forms import UserForm, LoginForm
from .views import register, login_view, admin_register


class UserViewTests(TestCase):

    def setUp(self):
        # Setup code for the tests, like creating a user or a group if needed
        # self.admin_group = Group.objects.create(name='AdminGroup')
        User.objects.create_user(username='testuser1', password='testpassword123', email='test@example.com')

    def test_register_view_post_success(self):
        # Test successful registration
        response = self.client.post(reverse('register:register'), {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'new@example.com',
            'currency': 'gbp'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(self.client.login(username='newuser', password='newpassword123'))

    def test_register_view_post_invalid(self):
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

    def test_admin_register_view_post_success(self):
        # Test successful admin registration
        self.client.login(username='admin1', password='admin1')
        response = self.client.post(reverse('register:admin_register'), {
            'username': 'adminuser',
            'password1': 'adminpassword123',
            'password2': 'adminpassword123',
            'email': 'admin@example.com',
            'currency': 'gbp'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        new_admin = User.objects.get(username='adminuser')
        self.assertTrue(new_admin.groups.filter(name='AdminGroup').exists())
