from django.contrib import admin
from .models import Profile
from  .models import Post ,Likepost,FollowersCount
# Register your models here.

#make profile registery on admin panel
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Likepost)
admin.site.register(FollowersCount)