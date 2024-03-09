from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import PasswordInput

from payapp.models import Account
from payapp.utils import convert_currency
from django_password_eye.fields import PasswordEye


class UserForm(UserCreationForm):
    """
    Form for creating a new user and account
    """
    # Add a currency field to the form using the currency choices from the Account model
    currency = forms.ChoiceField(choices=Account.CURRENCY_CHOICES, required=True,
                                 label='Currency')

    class Meta:
        """
        Meta class to specify the model and fields to be used in the form
        """
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'currency']

    def __init__(self, *args, **kwargs):
        """
        Constructor method to set the required fields
        :param args:
        :param kwargs:
        """
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        self.fields['currency'].required = True



    def save(self, commit=True):
        """
        Saves the user and creates an account for the user

        :param commit:
        :return:
        """
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            account = Account(user=user, currency=self.cleaned_data['currency'])
            if account.currency != "gbp":
                account.balance = convert_currency("GBP", account.currency, 1000)
            user.save()
            account.save()
        return user


class LoginForm(forms.Form):
    """
    Form for logging in a user
    """
    username = forms.CharField()
    password = forms.CharField(widget=PasswordInput)

