from django.urls import path
from . import views
from user import views as user_views
from django.contrib.auth import views as auth_views

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
    path('comment-replies/<int:pk>/',views.ReplyCommentView.as_view(),name='comment_replies'),
    path('comment-delete/<int:pk>/',views.DeleteComment.as_view(),name='comment_delete'),
    path('comment-update/<int:pk>',views.UpdateComment.as_view(),name='comment_update'),

    # Event Attendance URLs
    path('attend/<int:pk>/', views.EventAttendanceView.as_view(), name='attend_event'),
    path('chatroom/<int:pk>/',views.ChatRoomView.as_view(),name='chat_room'),
    path('report-event/<int:pk>/',views.ReportView.as_view(),name='report_event'),

    # Notification URLs
    path('notifications/', user_views.ListNotification.as_view(), name='notification_list'),
    path('create-notification/<int:event_id>/', user_views.CreateNotification.as_view(), name='create_notification'),
    path('detail-notification/<int:pk>/', user_views.DetailNotification.as_view(), name='detail_notification'),


    #UserConnection URLs
    path('user-connection',user_views.CreateUserConnection.as_view(),name='user_connection'),
    path('list-followers',user_views.ListFollowers.as_view(),name='list_followers'),
    path('list-following',user_views.ListFollowing.as_view(),name='list_followings'),


    #Batches URLs
   # Batches URLs
    path('create-batch/', user_views.CreateBatch.as_view(), name='create_batch'),
    path('list-batch/', user_views.ListBatch.as_view(), name='list_batch'),
    path('detail-batch/<int:pk>/', user_views.DetailBatch.as_view(), name='detail_batch'),
    path('delete-batch/<int:pk>/', user_views.DeleteBatch.as_view(), name='delete_batch'),
    path('list-user-batch/', user_views.ListUserBatch.as_view(), name='list_user_batch'),

        
]