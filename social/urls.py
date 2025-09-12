from django.urls import path
from . import views

# Keep app_name only if you also namespace when including (see note below)
app_name = 'social'

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('signup/', views.signup_view, name='signup'),
    path('u/<str:username>/', views.profile_view, name='profile'),
    path('u/<str:username>/follow/', views.follow, name='follow'),
    path('u/<str:username>/unfollow/', views.unfollow, name='unfollow'),
    path('account/delete/', views.account_delete, name='account_delete'),
    path('post/create/', views.create_post, name='post-create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post-edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
    path('post/<int:pk>/<str:action>/', views.post_react, name='post-react'),
    path('post/<int:pk>/share/', views.post_share, name='post-share'),
    path('post/<int:pk>/reply/', views.post_reply, name='post-reply'),
    path('users/', views.users_list, name='users'),
    path('explore/', views.posts_explore, name='explore'),

]
