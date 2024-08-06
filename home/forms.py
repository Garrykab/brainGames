from django import forms

class LoginForm(forms.Form):
    username = forms.ChoiceField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.ChoiceField(widget=forms.PasswordInput(attrs={'class':'form-control'}))