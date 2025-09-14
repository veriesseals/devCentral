from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.http import require_POST
from collections import defaultdict
from .utils import render_markdown
from .forms import (
    SignUpForm, PostForm, ReplyForm, ProfileForm,
    CodeSnippetForm, AccountDeleteForm
)
from .models import Post, Reply, CodeSnippet, Follow
from django.urls import reverse  # <-- ensure this import exists
from django.db.models import Prefetch


User = get_user_model()

# -----------------------
# Auth / Signup
# -----------------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            p = user.profile
            p.bio = form.cleaned_data.get('bio', '')
            if form.cleaned_data.get('avatar'):
                p.avatar = form.cleaned_data['avatar']
            p.save()
            login(request, user)
            return redirect('social:feed')
        else:
            messages.error(request, f"Sign up failed. Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

# -----------------------
# Feed
# -----------------------
@login_required
def feed_view(request):
    following_ids = request.user.following.values_list('id', flat=True)
    posts = (Post.objects
            .select_related('author', 'author__profile')
            .filter(Q(author=request.user) | Q(author__id__in=following_ids))
            .order_by('-created_at'))

    for p in posts:
        p.rendered_html = render_markdown(p.body)

    all_users = (User.objects
                .select_related('profile')
                .exclude(id=request.user.id)
                .order_by('username'))

    # collect replies for these posts (works regardless of related_name)
    post_ids = [p.id for p in posts]
    reply_map = defaultdict(list)
    for r in Reply.objects.filter(post_id__in=post_ids).select_related('author', 'author__profile'):
        reply_map[r.post_id].append(r)

    for p in posts:
        p.reply_list = reply_map.get(p.id, [])
        p.reply_count = len(p.reply_list)

    context = {
        'posts': posts,
        'post_form': PostForm(),
        'reply_form': ReplyForm(),
        'all_users': all_users,
    }
    # Your files are at social/templates/*.html → render without the "social/" prefix
    return render(request, 'feed.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        f = PostForm(request.POST, request.FILES)
        if f.is_valid():
            obj = f.save(commit=False)
            obj.author = request.user
            obj.save()
    return redirect('social:feed')

# -----------------------
# Posts (edit / delete / reply / react / share)
# -----------------------
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
            return redirect('social:profile', username=request.user.username)
    else:
        form = PostForm(instance=post)
    return render(request, 'post_edit.html', {'form': form, 'post': post})


@login_required
def post_reply(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    post = get_object_or_404(Post, pk=pk)

    # where to go back (defaults to feed)
    next_url = request.POST.get("next")
    if not next_url:
        next_url = reverse("social:feed")

    body = (request.POST.get("body") or "").strip()
    if not body:
        messages.error(request, "Reply can’t be empty.")
        return redirect(next_url)

    try:
        Reply.objects.create(post=post, author=request.user, body=body)
        messages.success(request, "Reply posted.")
    except Exception as e:
        messages.error(request, f"Couldn’t post reply: {e!s}")

    return redirect(next_url)


@login_required
def post_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You can only delete your own posts.")
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect('social:profile', username=request.user.username)

@login_required
def post_react(request, pk, action):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    post = get_object_or_404(Post, pk=pk)
    if action == "like":
        Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") + 1)
    elif action == "dislike":
        Post.objects.filter(pk=post.pk).update(dislikes_count=F("dislikes_count") + 1)
    return redirect(request.POST.get("next") or "social:feed")

@login_required
def post_share(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    post = get_object_or_404(Post, pk=pk)
    Post.objects.filter(pk=post.pk).update(shares_count=F("shares_count") + 1)
    return redirect(request.POST.get("next") or "social:feed")

# -----------------------
# Code Snippets
# -----------------------
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
            return redirect('social:profile', username=request.user.username)
    else:
        form = CodeSnippetForm(instance=snippet)
    return render(request, 'snippet_edit.html', {'form': form, 'snippet': snippet})

@login_required
def snippet_create(request):
    if request.method == "POST":
        form = CodeSnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.author = request.user
            snippet.save()
            messages.success(request, "Code snippet posted.")
            return redirect('social:profile', username=request.user.username)
    else:
        form = CodeSnippetForm()
    return render(request, 'snippet_edit.html', {'form': form})

@login_required
def snippet_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    snippet = get_object_or_404(CodeSnippet, pk=pk)
    if snippet.author != request.user:
        return HttpResponseForbidden("You can only delete your own code snippets.")
    snippet.delete()
    messages.success(request, "Code snippet deleted.")
    return redirect('social:profile', username=request.user.username)

# -----------------------
# Follow / Unfollow
# -----------------------
@require_POST
@login_required
def follow(request, username):
    target = get_object_or_404(User, username=username)

    if request.user == target:
        messages.info(request, "You can't follow yourself.")
    else:
        # Idempotent: M2M add won't duplicate
        target.profile.followers.add(request.user)
        messages.success(request, f"You’re now following @{target.username}.")

    next_url = (request.POST.get("next")
                or request.META.get("HTTP_REFERER")
                or reverse("social:profile", args=[username]))
    return redirect(next_url)

@require_POST
@login_required
def unfollow(request, username):
    target = get_object_or_404(User, username=username)

    if request.user == target:
        messages.info(request, "You can't unfollow yourself.")
    else:
        target.profile.followers.remove(request.user)
        messages.info(request, f"You unfollowed @{target.username}.")

    next_url = (request.POST.get("next")
                or request.META.get("HTTP_REFERER")
                or reverse("social:profile", args=[username]))
    return redirect(next_url)

# -----------------------
# Profiles
# -----------------------

@login_required
@login_required
def profile(request, username):
    profile_user = get_object_or_404(User.objects.select_related("profile"), username=username)

    # Followers: Users who follow this profile_user
    followers = profile_user.profile.followers.select_related("profile").order_by("username")
    follower_count = followers.count()

    # Following: Profiles that THIS user follows (Profile queryset)
    following_profiles = profile_user.following.select_related("user", "user__profile").order_by("user__username")
    following_count = following_profiles.count()

    # Is the current viewer following this profile?
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = profile_user.profile.followers.filter(pk=request.user.pk).exists()

    # User's posts
    posts = (Post.objects
             .filter(author=profile_user)
             .select_related('author', 'author__profile')
             .order_by('-created_at'))

    for p in posts:
        try:
            p.rendered_html = render_markdown(p.body)
        except Exception:
            p.rendered_html = None

    # Attach replies (optional but keeps consistent with feed/explore)
    post_ids = [p.id for p in posts]
    reply_map = defaultdict(list)
    for r in (Reply.objects
              .filter(post_id__in=post_ids)
              .select_related('author', 'author__profile')
              .order_by('created_at')):
        reply_map[r.post_id].append(r)
    for p in posts:
        p.reply_list = reply_map.get(p.id, [])
        p.reply_count = len(p.reply_list)

    # Edit form only for the owner
    form = ProfileForm(instance=request.user.profile) if request.user == profile_user else None
    if request.method == 'POST' and form:
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('social:profile', username=profile_user.username)

    return render(request, "profile.html", {
        "profile_user": profile_user,
        "followers": followers,
        "follower_count": follower_count,
        "following": following_profiles,
        "following_count": following_count,
        "is_following": is_following,
        "posts": posts,
        "reply_form": ReplyForm(),
        "form": form,
    })


# -----------------------
# Account delete
# -----------------------
@login_required
def account_delete(request):
    if request.method == 'POST':
        form = AccountDeleteForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data['password']
            if request.user.check_password(pwd):
                username = request.user.username
                request.user.delete()
                messages.success(request, f"Account @{username} deleted.")
                logout(request)
                return redirect('login')  # auth login name
            else:
                messages.error(request, "Password incorrect. Please try again.")
    else:
        form = AccountDeleteForm()
    return render(request, 'account_delete.html', {'form': form})

# -----------------------
# Directories / Explore
# -----------------------
@login_required
def users_list(request):
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'users_list.html', {'users': users})

@login_required
def posts_explore(request):
    qs = (Post.objects
          .select_related('author', 'author__profile')
          .order_by('-created_at'))

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    posts = list(page_obj.object_list)

    # Render markdown (safe fallback)
    for p in posts:
        try:
            p.rendered_html = render_markdown(p.body)
        except Exception:
            p.rendered_html = None

    # ----- attach replies without relying on related_name -----
    post_ids = [p.id for p in posts]
    reply_map = defaultdict(list)
    for r in (Reply.objects
              .filter(post_id__in=post_ids)
              .select_related('author', 'author__profile')
              .order_by('created_at')):
        reply_map[r.post_id].append(r)

    for p in posts:
        p.reply_list = reply_map.get(p.id, [])
        p.reply_count = len(p.reply_list)
    # ----------------------------------------------------------

    return render(request, 'explore.html', {
        'page_obj': page_obj,
        'posts': posts,
        'reply_form': ReplyForm(),  # not used to submit, but fine to render
    })

# -----------------------
# Public feed fallback (kept if you still route it)
# -----------------------
def feed(request):
    posts = Post.objects.all()
    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        posts = Post.objects.filter(
            Q(author__in=following_ids) | Q(author=request.user)
        ).order_by('-created_at')
    return render(request, 'feed.html', {'posts': posts})
