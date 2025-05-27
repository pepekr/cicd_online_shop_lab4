from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None  # define attribute here to avoid warnings

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("No user with this email.")
            self.user = authenticate(username=user.username, password=password)
            if self.user is None:
                raise forms.ValidationError("Incorrect password.")
        return self.cleaned_data
