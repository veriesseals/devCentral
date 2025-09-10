from django.contrib import admin
from django.contrib import admin
from .models import Profile, Post, Reply, Reaction, Share



# Register your models here.
admin.site.register([Profile, Post, Reply, Reaction, Share])
