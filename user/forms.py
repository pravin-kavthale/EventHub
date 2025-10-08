from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile 

class UserRegisterForm(UserCreationForm):
    email=forms.EmailField()

    class Meta:
        model=User
        fields=['username','email','password1','password2']

class UserUpdateForm(forms.ModelForm):  
    email=forms.EmailField()
    class Meta:
        model=User
        fields=['username','email']
        fields=['username','email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=['FullName','Bio','Age','Gender','image','MobileNumber','is_private']
        widgets = {
            'FullName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'Bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Bio'}),
            'Age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'Gender': forms.Select(attrs={'class': 'form-control'}),
            'MobileNumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }




        
