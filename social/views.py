from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .forms import SignUpForm, PostForm, ReplyForm, ProfileForm
from .models import Post, Reaction, Share

# signup view
# -----------------------------------------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            p = user.profile
            p.bio = form.cleaned_data.get('bio','')
            if form.cleaned_data.get('avatar'):
                p.avatar = form.cleaned_data['avatar']
            p.save()
            login(request, user)
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

# feed view (posts from user and followed users)
# -----------------------------------------------
@login_required
def feed_view(request):
    following_ids = request.user.following.values_list('id', flat=True)
    posts = Post.objects.filter(Q(author=request.user) | Q(author__id__in=following_ids)).order_by('-created_at')
    return render(request, 'feed.html', {'posts': posts, 'post_form': PostForm(), 'reply_form': ReplyForm()})

# create post view
# -----------------------------------------------
@login_required
def create_post(request):
    if request.method == 'POST':
        f = PostForm(request.POST, request.FILES)
        if f.is_valid():
            obj = f.save(commit=False)
            obj.author = request.user
            obj.save()
    return redirect('feed')

# add reply view
# -----------------------------------------------
@login_required
def add_reply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        f = ReplyForm(request.POST)
        if f.is_valid():
            r = f.save(commit=False)
            r.post = post; r.author = request.user; r.save()
    return redirect('feed')

# react (like/dislike) view
# -----------------------------------------------
@login_required
def react(request, post_id, kind):
    post = get_object_or_404(Post, id=post_id)
    # toggle
    q = Reaction.objects.filter(post=post, user=request.user, kind=kind)
    if q.exists(): q.delete()
    else: Reaction.objects.create(post=post, user=request.user, kind=kind)
    return redirect('feed')

# share post view
# -----------------------------------------------
@login_required
def share_post(request, post_id):
    Share.objects.create(post_id=post_id, user=request.user)
    messages.success(request, 'Post shared!')
    return redirect('feed')

# follow/unfollow view
# -----------------------------------------------
@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    prof = target.profile
    if request.user in prof.followers.all(): prof.followers.remove(request.user)
    else: prof.followers.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('feed')))

# profile view (with edit option if own profile)
# -----------------------------------------------
@login_required
def profile_view(request, username):
    u = get_object_or_404(User, username=username)
    is_following = request.user in u.profile.followers.all()
    posts = u.posts.order_by('-created_at')
    form = ProfileForm(instance=request.user.profile) if request.user==u else None
    if request.method=='POST' and form:
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid(): form.save(); return redirect('profile', username=u.username)
    return render(request, 'profile.html', {'profile_user': u, 'is_following': is_following, 'posts': posts, 'form': form})
