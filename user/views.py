from django.shortcuts import render

from django.controb.auth.forms import UserCreationForm

def register(request):
    form=UserCreationForm()
    return render(request,'user/register.html',{'form':form})

# Create your views here.
