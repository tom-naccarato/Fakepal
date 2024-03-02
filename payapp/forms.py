from django import forms
from payapp.models import Request


class RequestForm(forms.ModelForm):

    class Meta:
        model = Request
        fields = ['receiver', 'amount']
        widgets = {

            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

