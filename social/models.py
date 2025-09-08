from django.conf import settings
from django.db import models
from django.utils import timezone
User = settings.AUTH_USER_MODEL

# Helper functions for upload paths
# -----------------------------------------------
def avatar_upload_path(instance, filename):
    return f'avatars/{instance.user.id}/{filename}'

def post_upload_path(instance, filename):
    return f'posts/{instance.user.id}/{filename}'




# Create your models here.
# -----------------------------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    


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

