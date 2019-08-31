from django.urls import path

from . import views

urlpatterns = [
    path('api/enter_chat_room', views.enter_chat_room, name='enter_chat_room'),
    path('api/user_sign_up', views.user_sign_up, name='user_sign_up'),
    path('api/check_logged_in', views.check_logged_in, name='check_logged_in'),
    path('api/create_new_post', views.create_new_post, name='create_new_post'),
    path('api/like_a_post', views.like_a_post, name='like_a_post'),
    path('api/delete_a_post', views.delete_a_post, name='delete_a_post'),
    path('api/add_a_comment', views.add_a_comment, name='add_a_comment'),
    path('api/read_notifications', views.read_notifications, name='read_notifications'),
    path('api/follow_user', views.follow_user, name='follow_user'),
    path('api/get_feed_posts', views.get_feed_posts, name='get_feed_posts'),
    path('api/get_user_profile', views.get_user_profile, name='get_user_profile'),
    path('api/check_profile_name_availability', views.check_profile_name_availability, name='check_profile_name_availability'),
    path('api/upload_picture', views.upload_picture, name='upload_picture'),
    path('api/search', views.search, name='search'),
]