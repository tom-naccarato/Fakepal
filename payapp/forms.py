from django import forms
from django.contrib.auth.models import User

from payapp.models import Request, Account, Transfer


class RequestForm(forms.ModelForm):
    """
    Form to request money from another user
    """
    receiver = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Request
        fields = ['receiver', 'amount']
        widgets = {
            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'autocomplete': 'off',
                                               'min': '0.01'})
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor to set the label of the amount field to the user's currency
        :param args:
        :param kwargs:
        """
        user_currency = kwargs.pop('user_currency', None)  # get the user's currency
        super(RequestForm, self).__init__(*args, **kwargs)
        if user_currency:  # if the user's currency is known
            self.fields['amount'].label = f"Amount (in {user_currency.upper()})"  # set the label to the user's currency

    def clean_receiver(self):
        username = self.cleaned_data.get('receiver')
        try:
            user = User.objects.get(username=username)
            account = Account.objects.get(user=user)
            return account
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")


class PaymentForm(forms.ModelForm):
    """
    Form to make a payment to another user
    """
    receiver = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        """
        Meta Class to specify the model and fields to be used in the form
        """
        model = Transfer
        fields = ['receiver', 'amount']
        widgets = {
            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'autocomplete': 'off',
                                               'min': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Constructor to set the label of the amount field to the user's currency
        :param args:
        :param kwargs:
        """
        user_currency = kwargs.pop('user_currency', None)  # get the user's currency
        super(PaymentForm, self).__init__(*args, **kwargs)
        if user_currency:  # if the user's currency is known
            self.fields['amount'].label = f"Amount (in {user_currency.upper()})"  # set the label to the user's currency

    def clean_receiver(self):
        username = self.cleaned_data.get('receiver')
        try:
            user = User.objects.get(username=username)
            account = Account.objects.get(user=user)
            return account
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")
