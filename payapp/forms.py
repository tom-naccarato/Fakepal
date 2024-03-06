from django import forms
from payapp.models import Request, Account


class RequestForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(queryset=Account.objects.all(),
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Request
        fields = ['receiver', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

