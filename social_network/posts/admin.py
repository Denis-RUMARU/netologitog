from django.contrib import admin

# Register your models here.
from posts.models import Post, Comment, Like

admin.site.register([Post, Comment, Like])