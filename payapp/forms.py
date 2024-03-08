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
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

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
        model = Transfer
        fields = ['receiver', 'amount']
        widgets = {
            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_receiver(self):
        username = self.cleaned_data.get('receiver')
        try:
            user = User.objects.get(username=username)
            account = Account.objects.get(user=user)
            return account
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")
