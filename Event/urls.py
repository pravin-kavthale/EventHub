from django.urls import path
from . import views
from user import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # User Authentication URLs
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('profile/<str:username>/', user_views.profile, name='user_profile'),
    path('ProfilePrivacy/<int:pk>/', user_views.ProfilePrivacy.as_view(), name='Profile_Privacy'),
    path('password-change/', user_views.password_change, name='password_change'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='user/password_reset.html',
            extra_context={'view_type': 'reset_form'}
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/password_reset.html',
            extra_context={'view_type': 'reset_done'}
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset.html',
            extra_context={'view_type': 'reset_confirm'}
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/password_reset.html',
            extra_context={'view_type': 'reset_complete'}
        ),
        name='password_reset_complete'
    ),

    # Event URLs
    path('create-event/', views.CreateEvent.as_view(), name='create_event'),
    path('events/', views.PersonalizedEventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetails.as_view(), name='event_detail'),
    path('event-update/<int:pk>/', views.EventUpdate.as_view(), name='event_update'),
    path('event-delete/<int:pk>/', views.EventDelete.as_view(), name='event_delete'),
    path('my-events/', views.MyEvents.as_view(), name='my_events'),
    path('joined-events/', views.joinedEvents.as_view(), name='joined_events'),
    # Category URLs
    path('create-category/', views.CreateCategory.as_view(), name='create_category'),
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('category-update/<int:pk>/', views.CategoryUpdate.as_view(), name='category_update'),
    path('category-delete/<int:pk>/', views.CategoryDelete.as_view(), name='category_delete'),
    #like URL and comment
    path('like/<int:pk>/',views.LikeView.as_view(),name='like_event'),
    path('comment/<int:pk>/',views.CommentView.as_view(),name='comment_event'),
    path('comment-delete/<int:pk>/',views.DeleteComment.as_view(),name='comment_delete'),
    path('comment-update/<int:pk>',views.UpdateComment.as_view(),name='comment_update'),
    path('events/<int:pk>/report/', views.ReportView.as_view(), name='event_report'),
    path('event_attendance/<int:pk>/', views.JoinEvent.as_view(), name='join_event'),
    # Event Attendance URLs
    path('attend/<int:pk>/', views.EventAttendanceView.as_view(), name='attend_event'),
    path('chatroom/<int:pk>/',views.ChatRoomView.as_view(),name='chat_room'),
    path('report-event/<int:pk>/',views.ReportView.as_view(),name='report_event'),
    path('attendance-list/<int:pk>/', views.getEventAttendance.as_view(), name='attendance_list'),
    # Notification URLs
    path('notifications/', user_views.ListNotification.as_view(), name='notification_list'),
     path("notifications/mark-all-read/", user_views.mark_all_notifications_read, name="mark_all_notifications_read"),
    #UserConnection URLs
    path('connect/<int:user_id>/', user_views.CreateUserConnection.as_view(), name='connect_user'),
    path('followers/<int:user_id>/', user_views.ListFollowers.as_view(), name='list_followers'),
    path('following/<int:user_id>/', user_views.ListFollowing.as_view(), name='list_followings'),
    #Batches URLs
    path('create-batch/', user_views.CreateBatch.as_view(), name='create_batch'),
    path('list-batch/', user_views.ListBatch.as_view(), name='list_batch'),
    path('detail-batch/<int:pk>/', user_views.DetailBatch.as_view(), name='detail_batch'),
    path('delete-batch/<int:pk>/', user_views.DeleteBatch.as_view(), name='delete_batch'),
    path('list-user-batch/', user_views.ListUserBatch.as_view(), name='list_user_batch'),

    #Search Urls
    path("search-events/", views.EventSearchView.as_view(), name="event_search"),
    path("sidebar/", views.sidebar_view, name="sidebar"),
        
]