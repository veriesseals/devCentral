# 4) Forms (signup, profile update, post, reply)
# -----------------------------------------------

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Reply


# Signup form
# -----------------------------------------------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required = True)
    first_name = forms.CharField(max_length = 30)
    last_name = forms.CharField(max_length = 30)
    bio = forms.CharField(max_length = 280, required = False)
    avatar = forms.ImageField(required = False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'bio', 'avatar')
        
# Profile update form
# -----------------------------------------------
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')
        
# Post form
# -----------------------------------------------
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('body','image')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'What\'s on your mind?'})
        }
        
# Reply form
# -----------------------------------------------
class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'})
        }