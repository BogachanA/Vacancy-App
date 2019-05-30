from django import forms
from classAvailable.models import Reservation


class loginForm(forms.Form):
    auto_id=False

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Kullanıcı Adın',}),max_length=100,required=True,label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Şifren'}),label='')