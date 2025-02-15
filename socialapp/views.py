from django.shortcuts import render
from django.contrib.auth.models import User , auth
from django.contrib import messages
from django.http import HttpResponse
from .models import Profile,Post,Likepost,FollowersCount
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
# Create your views here.

@login_required(login_url='login')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    user_following_list = []
    feed = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)
    for username in user_following:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)
    feed_list = list(chain(*feed))
    posts = Post.objects.all()
    
    #user_suggestions
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(usrid=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    
   
    return render(request,'index.html',{'user_profile':user_profile,'posts':feed_list,'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required
def like(request):
     username = request.user.username
     post_id = request.GET.get('post_id')

     post = Post.objects.get(id=post_id)

     like_filter = Likepost.objects.filter(post_id=post_id, username=username).first()

     if like_filter == None:
        new_like = Likepost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_likes = post.no_likes+1
        post.save()
        return redirect('/')
     else:
        like_filter.delete()
        post.no_likes = post.no_likes-1
        post.save()
        return redirect('/')


@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email'] 
        password = request.POST['pwd']
        confirm_password = request.POST['cpwd']   
        
        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request,"Email Is Already In Use!")
            elif User.objects.filter(username=username).exists():
                    messages.info(request,"Username Already Taken")
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
               # log user in and redirect to settings 
                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)
               #creaete profile object for the new user
                user_model = User.objects.get(username=username) 
                new_profile = Profile.objects.create(user=user_model,usrid=user_model.id)
                new_profile.save()
                return redirect('signup')
        else:
            messages.info(request,"password did not match!")
            return redirect('signup')        
    else:
        return render(request,'signup.html')
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pwd']
        
        user = auth.authenticate(username=username,password=password)
        if user is not None:
           auth.login(request,user)
           return redirect('/')
        else:
           messages.info(request,'credentials invalid')
           return redirect('login') 
    else:
        return render(request,'signin.html')   

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')
def upload(request):
    if request.method == 'POST' :
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['Caption']
        new_post = Post.objects.create(user=user,image=image,caption=caption)
        new_post.save()
         
        return redirect('/')
        
    else:    
        return redirect('/')
def profile(request,pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    
    follower = request.user.username
    user = pk
    
    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
        
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(user=pk))
        
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length':user_post_length,
        'button_text':button_text,
        'user_followers': user_followers,
        'user_following':user_following
    }
    return render(request,'profile.html',context)

def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        
        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        redirect('/')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(usrid=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})
