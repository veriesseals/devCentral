from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# If you have a custom user model, use settings.AUTH_USER_MODEL
# -----------------------------------------------
User = settings.AUTH_USER_MODEL

# Helper functions for upload paths
# -----------------------------------------------

# Models
# -----------------------------------------------
def avatar_upload_path(instance, filename):
    return f'avatars/{instance.user_id}/{filename}'

def post_upload_path(instance, filename):
    # Use the Post.author FK, not user
    author_id = getattr(instance, 'author_id', None)
    if not author_id and getattr(instance, 'author', None):
        try:
            author_id = instance.author.pk
        except Exception:
            author_id = 'tmp'
    return f'posts/{author_id or "tmp"}/{filename}'


# Profile model
# -----------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    bio = models.CharField(max_length=280, blank=True)
    followers = models.ManyToManyField('auth.User', related_name='following', blank=True)
    
    def __str__(self): return self.user.username

# Post model with reactions and shares
# -----------------------------------------------
class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='posts')
    body = models.TextField(max_length=1000)
    image = models.ImageField(upload_to=post_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # ✅ add these three fields
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_posts", blank=True)
    shares_count = models.PositiveIntegerField(default=0)
    
    # in social/models.py inside Post model
    likes_count = models.PositiveIntegerField(default=0)
    
    dislikes_count = models.PositiveIntegerField(default=0)
    
    shares_count = models.PositiveIntegerField(default=0)


# Reply model for comments on posts
# -----------------------------------------------
class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)

# Reaction model for likes/dislikes
# -----------------------------------------------
class Reaction(models.Model):
    LIKE, DISLIKE = 'like','dislike'
    KIND_CHOICES = [(LIKE,'Like'),(DISLIKE,'Dislike')]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    kind = models.CharField(max_length=7, choices=KIND_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta: unique_together = ('post','user','kind')

# Share model for sharing posts
# -----------------------------------------------
class Share(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)


# Create CodeSnippet model for sharing code snippets
# -----------------------------------------------
# --- ADD THIS if not present ---
class CodeSnippet(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="snippets")
    title = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=32, default="python")
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"{self.author.username} • {self.language}"
    
    
# Follow model to manage user follows
# -----------------------------------------------
class Follow(models.Model):
    follower  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} → {self.following}"

