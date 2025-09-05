from django.urls import path
from . import views
from user import views as user_views

urlpatterns = [
    path('',views.home,name='Event-home'),
    path('register/',user_views.register,name='register'),
]