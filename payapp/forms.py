from django import forms
from payapp.models import Request, Account


class RequestForm(forms.ModelForm):
    receiver = forms.ModelChoiceField(queryset=Account.objects.none(),  # Initialize with none, will update in __init__
                                      widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Request
        fields = ['receiver', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Exclude the current user's account from the queryset
            self.fields['receiver'].queryset = Account.objects.exclude(user=user)


