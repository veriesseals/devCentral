from django.conf import settings
from django.db import models
from django.utils import timezone
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
    def likes_count(self): return self.reactions.filter(kind=Reaction.LIKE).count()
    def dislikes_count(self): return self.reactions.filter(kind=Reaction.DISLIKE).count()
    def shares_count(self): return self.shares.count()

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
class CodeSnippet(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="snippets")
    title = models.CharField(max_length=100, blank=True)
    code = models.TextField()
    language = models.CharField(
        max_length=50,
        choices=[
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("java", "Java"),
            ("cpp", "C++"),
            ("csharp", "C#"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("sql", "SQL"),
        ],
        default="python"
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author.username} – {self.title or 'Untitled'}"

