from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Reply

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

# Reply form for comments
# -----------------------------------------------
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply; fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows':2,'placeholder':'Write a reply…'})}
