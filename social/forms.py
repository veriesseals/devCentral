from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Reply
from .models import Post
from .models import Post, CodeSnippet  # <-- include CodeSnippet

# Forms
# -----------------------------------------------

# Signup form extending UserCreationForm
# Includes avatar upload and bio
# -----------------------------------------------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    bio = forms.CharField(max_length=280, required=False)
    avatar = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2','bio','avatar')

# Profile edit form
# -----------------------------------------------
class ProfileForm(forms.ModelForm):
    class Meta: model = Profile; fields = ('bio','avatar')

# Post creation form
# -----------------------------------------------
class PostForm(forms.ModelForm):
    class Meta:
        model = Post; fields = ('body','image')
        widgets = {'body': forms.Textarea(attrs={'rows':3,'placeholder':'Share something…'})}
        
# --- ADD THIS: CodeSnippetForm ---
LANGUAGE_CHOICES = [
    ("python", "Python"),
    ("javascript", "JavaScript"),
    ("typescript", "TypeScript"),
    ("java", "Java"),
    ("c", "C"),
    ("cpp", "C++"),
    ("csharp", "C#"),
    ("go", "Go"),
    ("php", "PHP"),
    ("ruby", "Ruby"),
    ("swift", "Swift"),
    ("kotlin", "Kotlin"),
    ("rust", "Rust"),
    ("sql", "SQL"),
    ("bash", "Bash / Shell"),
    ("html", "HTML"),
    ("css", "CSS"),
    ("json", "JSON"),
    ("yaml", "YAML"),
    ("dockerfile", "Dockerfile"),
    ("powershell", "PowerShell"),
    ("plaintext", "Plain text"),
]

class CodeSnippetForm(forms.ModelForm):
    class Meta:
        model = CodeSnippet
        fields = ["title", "language", "code"]
        widgets = {
            "code": forms.Textarea(attrs={"rows": 10, "spellcheck": "false"}),
        }

# Reply form for comments
# -----------------------------------------------
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply; fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows':2,'placeholder':'Write a reply…'})}

# Account deletion form
# -----------------------------------------------
class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        label="Confirm your password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )