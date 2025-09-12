from django.contrib import messages
from django.contrib.auth import login, logout

from django.contrib.auth.models import User
from django.db.models import Q

from django.http import HttpResponseRedirect

from django.urls import reverse
from .utils import render_markdown # if you’re using server-side markdown
from social.utils import render_markdown 
from .forms import SignUpForm, PostForm, ReplyForm, ProfileForm
from .models import Post, Reaction, Share
from .models import Post, CodeSnippet
from .forms import PostForm, CodeSnippetForm
from .models import Post, Reply  # adjust if your Reply model is elsewhere
from .forms import ReplyForm

# --- add these imports at the top if not present ---
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render

from .models import Post  # ensure Post is imported

from .models import Follow  # ensure this import exists
from .forms import AccountDeleteForm

from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST      # ← ADD THIS

User = get_user_model()

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
    for p in posts:
        p.rendered_html = render_markdown(p.body)
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

# edit post view
# -----------------------------------------------
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You can only edit your own posts.")
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated.")
            return redirect('profile', username=request.user.username)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form, 'post': post})

@login_required
def post_reply(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    post = get_object_or_404(Post, pk=pk)
    form = ReplyForm(request.POST)
    if form.is_valid():
        r = form.save(commit=False)
        r.post = post
        r.author = request.user
        r.save()
    return redirect(request.POST.get("next") or "feed")

# delete post view
# -----------------------------------------------
@login_required
def post_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You can only delete your own posts.")
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect('profile', username=request.user.username)


# create code snippet view
# -----------------------------------------------
@login_required
def snippet_edit(request, pk):
    snippet = get_object_or_404(CodeSnippet, pk=pk)
    if snippet.author != request.user:
        return HttpResponseForbidden("You can only edit your own code snippets.")
    if request.method == "POST":
        form = CodeSnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            messages.success(request, "Code snippet updated.")
            return redirect('profile', username=request.user.username)
    else:
        form = CodeSnippetForm(instance=snippet)
    return render(request, 'snippet_edit.html', {'form': form, 'snippet': snippet})

# create code snippet view
# -----------------------------------------------
@login_required
def snippet_create(request):
    if request.method == "POST":
        form = CodeSnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.author = request.user
            snippet.save()
            messages.success(request, "Code snippet posted.")
            return redirect('profile', username=request.user.username)
    else:
        form = CodeSnippetForm()
    return render(request, 'snippet_edit.html', {'form': form})  # reuse template

# delete code snippet view
# -----------------------------------------------
@login_required
def snippet_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    snippet = get_object_or_404(CodeSnippet, pk=pk)
    if snippet.author != request.user:
        return HttpResponseForbidden("You can only delete your own code snippets.")
    snippet.delete()
    messages.success(request, "Code snippet deleted.")
    return redirect('profile', username=request.user.username)

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
def post_react(request, pk, action):
    """
    Handles like/dislike for a Post by incrementing counters.
    Expects POST only. Redirects back to ?next= or 'feed'.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    post = get_object_or_404(Post, pk=pk)

    if action == "like":
        Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") + 1)
    elif action == "dislike":
        Post.objects.filter(pk=post.pk).update(dislikes_count=F("dislikes_count") + 1)
    else:
        # unknown action: just ignore and bounce back
        pass

    return redirect(request.POST.get("next") or "feed")

# share post view
# -----------------------------------------------
@login_required
def post_share(request, pk):
    """
    Handles share count for a Post. POST only.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    post = get_object_or_404(Post, pk=pk)
    Post.objects.filter(pk=post.pk).update(shares_count=F("shares_count") + 1)

    return redirect(request.POST.get("next") or "feed")

# follow/unfollow view
# -----------------------------------------------
@login_required
def follow_toggle(request, username):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('profile', username=username)
    profile = target.profile
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)
    return redirect('profile', username=target.username)

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


# follow/unfollow shortcuts
# -----------------------------------------------
@login_required
def follow(request, username):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    target = get_object_or_404(User, username=username)
    if target != request.user:
        target.profile.followers.add(request.user)
    return redirect('profile', username=username)

@login_required
def unfollow(request, username):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    target = get_object_or_404(User, username=username)
    if target != request.user:
        target.profile.followers.remove(request.user)
    return redirect('profile', username=username)

def feed(request):
    """
    Home feed:
      - If logged in: show your posts + posts of people you follow
      - If logged out: show all posts or a landing page
    """
    from .models import Post  # only if you have Post in this app
    posts = Post.objects.all()
    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        posts = Post.objects.filter(Q(author__in=following_ids) | Q(author=request.user)).order_by('-created_at')
    return render(request, 'social/feed.html', {'posts': posts})

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_self = (request.user.is_authenticated and request.user.pk == profile_user.pk)
    is_following = False
    if request.user.is_authenticated and not is_self:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    return render(request, 'social/profile.html', {
        'profile_user': profile_user,
        'is_self': is_self,
        'is_following': is_following,
        'follower_count': follower_count,
        'following_count': following_count,
    })

@require_POST
@login_required
def follow(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Follow.objects.get_or_create(follower=request.user, following=target)
        messages.success(request, f"You’re now following @{target.username}.")
    return redirect('social:profile', username=target.username)

@require_POST
@login_required
def unfollow(request, username):
    target = get_object_or_404(User, username=username)
    if target != request.user:
        Follow.objects.filter(follower=request.user, following=target).delete()
        messages.success(request, f"You unfollowed @{target.username}.")
    return redirect('social:profile', username=target.username)

@login_required
def account_delete(request):
    """
    Delete the current user after password confirmation.
    """
    if request.method == 'POST':
        form = AccountDeleteForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data['password']
            if request.user.check_password(pwd):
                username = request.user.username
                request.user.delete()
                messages.success(request, f"Account @{username} deleted.")
                # logged-out automatically when user row is gone; ensure session cleared
                logout(request)
                return redirect('login')
            else:
                messages.error(request, "Password incorrect. Please try again.")
    else:
        form = AccountDeleteForm()
    return render(request, 'social/account_delete.html', {'form': form})