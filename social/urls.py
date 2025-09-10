from django.urls import path
from . import views

# url patterns for the social app
# -----------------------------------------------
urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('signup/', views.signup_view, name='signup'),
    path('post/create/', views.create_post, name='post-create'),
    path('post/<int:post_id>/reply/', views.add_reply, name='post-reply'),
    path('post/<int:post_id>/<str:kind>/', views.react, name='post-react'),   # like|dislike
    path('post/<int:post_id>/share/', views.share_post, name='post-share'),
    path('u/<str:username>/', views.profile_view, name='profile'),
    path('u/<str:username>/follow/', views.toggle_follow, name='follow-toggle'),
]
