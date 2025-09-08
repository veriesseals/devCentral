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

def signup_view(request):
    pass
