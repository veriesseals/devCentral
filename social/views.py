# 5) Views (feed, signup, post, react, follow, share, profile)from django.contrib import messages

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import SignUpForm, PostForm, ReplyForm, ProfileForm
from .models import Post, Reaction, Share, Profile

# Create your views here.
# -----------------------------------------------


# Created signup_view
# -----------------------------------------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Create a Profile instance for the new user
            user = form.save()
            profile = user.profile
            profile.bio = form.cleaned_data.get('bio', '')
            avatar = form.cleaned_data.get('avatar')
            if avatar:
                profile.avatar = avatar
            profile.save()
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

# Created feed_view
# -----------------------------------------------
@login_required
def feed_view(request):
    # Get posts from users the current user is following or their own posts
    following_ids = request.user.profile.following.values_list('id', flat = True)
    posts = Post.objects.filter(Q(author=request.user) | Q(author__id__in=following_ids)).order_by('-created_at')
    post_form = PostForm()
    reply_form = ReplyForm()
    return render(request, 'feed.html', {'posts': posts, 'post_form': post_form, 'reply_form': reply_form})

