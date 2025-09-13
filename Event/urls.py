from django.urls import path
from . import views
from user import views as user_views

urlpatterns = [
    path('', views.home, name='Event-home'),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    # Event URLs
    path('create-event/', views.CreateEvent.as_view(), name='create_event'),
    path('events/', views.EventList.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetails.as_view(), name='event_detail'),
    path('event-update/<int:pk>/', views.EventUpdate.as_view(), name='event_update'),
    path('event-delete/<int:pk>/', views.EventDelete.as_view(), name='event_delete'),
    # Category URLs
    path('create-category/', views.CreateCategory.as_view(), name='create_category'),
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('category-update/<int:pk>/', views.CategoryUpdate.as_view(), name='category_update'),
    path('category-delete/<int:pk>/', views.CategoryDelete.as_view(), name='category_delete'),
    #like URL and comment
    path('like/<int:pk>/',views.LikeView.as_view(),name='like_event'),
    path('comment/<int:pk>/',views.CommentView.as_view(),name='comment_event'),
    path('comment_replies/<int:pk>/',views.CommentReplyView.as_view(),name='comment_replies'),
    # Event Attendance URLs
    path('attend/<int:pk>/', views.EventAttendanceView.as_view(), name='attend_event'),
    path('chatroom/<int:pk>/',views.ChatRoomView.as_view(),name='chat_room'),
]
