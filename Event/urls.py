from django.urls import path
from . import views
from user import views as user_views

urlpatterns = [
    path('',views.home,name='Event-home'),
    path('register/',user_views.register,name='register'),
    path('profile/',user_views.profile,name='profile'),
    
    # Event URLs
    path('create-event/', views.CreateEvent.as_view(), name='create_event'),
    path('events/', views.EventList.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetails.as_view(), name='event_detail'),
    path('event_update/<int:pk>/', views.EventUpdate.as_view(), name='event_update'),
    path('event_delete/<int:pk>/', views.EventDelete.as_view(), name='event_delete'),
]