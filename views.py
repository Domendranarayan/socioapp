# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render
from .models import FriendRequest, User
from .forms import UserCreateForm, AccountAuthenticationForm
from django.contrib.auth import (
    authenticate, login, logout
)
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from sociosite.settings import LOGIN_REDIRECT_URL
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import PostForm, UpdatePostForm, SearchForm
from .models import Post
from operator import attrgetter
from django.urls import reverse_lazy
from django.contrib import messages
import json

@login_required(login_url=LOGIN_REDIRECT_URL)
def home(request):
    obj = Post.objects.all()
    query = ""
    context={}
    if request.GET:
        query = request.GET.get('q', '')
        print(query)
        context['query'] = str(query)
    obj = sorted(get_blog_queryset(query), key=attrgetter('updated_at'), reverse=True)
    context['obj']  = obj

    return render(request, "base.html",context)



@login_required(login_url=LOGIN_REDIRECT_URL)
def create_post(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            form.save_m2m()
            messages.success(request, "Post Was Created with title {}".format(instance.title))
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            messages.error(request, "Please Correct Below Errors")
            print(form.errors)
            form = PostForm()
            return render(request, "app/create_post.html", {"form":form})
    context = {
    'form':form
    }

    return render(request, "app/create_post.html", context)
def user_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
    print(query)
    results = User.objects.annotate(search=SearchVector('name', 'email', 'phone'),).filter(search=query)
    print(results)
    if len(results)<0:
        return render(request, "base.html", {'form':form})
    else:
        return render(request,'app/search.html',{'form': form, 'query': query, 'results': results})


def post_detail(request, year, month, day, post):
    obj = get_object_or_404(Post, slug=post)
    user = request.user
    count_hit = True
    context = {
    'obj':obj,
    }
    
    return render(request, "app/post_detail.html",context)
@login_required(login_url=LOGIN_REDIRECT_URL)
def update_post(request, slug):
    context = {}
    user  = request.user
    post = get_object_or_404(Post, slug=slug)
    if request.method=='POST':
        form = UpdatePostForm(request.POST or None, request.FILES or None, instance=post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "updated"
            post = obj
            messages.success(request, "{} was updated".format(obj.title))
            return HttpResponseRedirect(post.get_absolute_url())


    form = UpdatePostForm(
    initial={
    'title':post.title,
    'content':post.content,
    'image':post.image,
    })

    context['form'] = form
    return render(request, "app/update_post.html", context)

class post_delete(DeleteView):
    model = Post
    template_name="app/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")
    success_message = "Post Deleted successfully"

@login_required(login_url=LOGIN_REDIRECT_URL)
def post_list(request):
    obj = Post.objects.all()
    query = ""
    context={}
    if request.GET:
        query = request.GET.get('q', '')
        print(query)
        context['query'] = str(query)
    obj = sorted(get_blog_queryset(query), key=attrgetter('updated'), reverse=True)
    context['obj']  = obj

    return render(request, "base.html", context)

@login_required(login_url=LOGIN_REDIRECT_URL)
def profile_page(request, phone):
    context={}
    print(User.objects.all())
    
    obj = User.objects.filter(phone=phone)
    all_users = User.objects.all()
    obj=obj[0]
    con_users = obj.friends.all()
    x = []
    requests = FriendRequest.objects.filter(to_user=request.user)
    for i in range(len(con_users)):
        mutual=[]
        for j in con_users[i].friends.all():

            if con_users[i].friends.all()  & request.user.friends.all() :
                mutual.append(con_users[i].friends.all()  & request.user.friends.all() )
        x.append(mutual)
    context={
        "requests":requests,
        "con_users":con_users,
        "obj":obj ,
        "all_users":all_users
    }
    return render(request, 'app/userprofile.html', context)





def get_blog_queryset(query=None):
    queryset = []
    queries=  query.split(" ")
    for q in queries :
        posts = Post.objects.filter(
            Q(title__icontains=q)|
            Q(content__icontains=q)
        ).distinct()
        for post in posts:
            queryset.append(post)
    return list(set(queryset))


@login_required(login_url=LOGIN_REDIRECT_URL)
def all_users(request):
    obj  = User.objects.exclude(user=request.user)
    context = {
        'users':obj

    }
    return render(request,  "app/users.html", context)

@login_required(login_url=LOGIN_REDIRECT_URL)
def friend_request(request):
    user=request.user
    obj = FriendRequest.objects.filter(to_user=user)
    print(obj)
    context={}
    context['frnd_requests']=obj
    return render(request, 'app/friend_requests.html', context)

@login_required(login_url=LOGIN_REDIRECT_URL)    
def friends(request):
    user=request.user
    obj = user.friends.all()
    print(obj)
    context={}
    context['friends'] = obj
    return render(request, "app/friends.html",context)

def signupview(request):
    if request.method=='POST':
        form=UserCreateForm(request.POST)
        if form.is_valid():
            new_user=form.save()
            new_user=authenticate(
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password1']
                )
            login(request, new_user)
            return redirect("home")
        else:
            print(request.POST, form.errors)
            form=UserCreateForm()
            return render(request, 'app/signup.html', {"form":form})
    else:
        form=UserCreateForm()
        return render(request, 'app/signup.html', {'form':form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged Out")
    return redirect("home")

def  loginview(request):
    context = {}

    user = request.user

    if user.is_authenticated:
        print("user authenticated")
        return redirect("home")
    if request.POST:
        form    = AccountAuthenticationForm(request.POST)
        phone   = request.POST.get('phone')
        password = request.POST.get('password')
        user =  authenticate(phone=phone, password=password)
        if user:
            login(request, user)
            messages.success(request, "Logged In")
            return redirect("home")
        else:

            print(request.POST, form.errors)
            return render(request, 'app/login.html', {'login_form':form})
            messages.error(request, "Please Correct Below Errors")
    else:
        form = AccountAuthenticationForm()
        context['login_form'] = form

        return render(request, "app/login.html", context)

@login_required(login_url=LOGIN_REDIRECT_URL)
def send_friend_request(request, userId):
    from_user = request.user
    to_user   = User.objects.get(id=userId)
    if from_user.phone ==to_user.phone:
        messages.success(request, "Cannot send friend request to Yourself")
        return redirect("profile", phone=request.user.phone)
    friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        messages.success(request, 'Friend Request sent')
        return redirect("profile", phone=request.user.phone)
    else:
        messages.error(request, 'Friend Request Was Already Sent')
        return redirect("profile", phone=request.user.phone)


@login_required(login_url=LOGIN_REDIRECT_URL)
def accept_friend_request(request, requestID):
    
    friend_request = FriendRequest.objects.get(id=requestID)
    if friend_request.to_user==request.user:
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.delete()
        messages.success(request,"Friend Request Accepted")
        return redirect("profile", phone=request.user.phone)
    else:
        messages.error(request, "Friend Request Not Accepted")
        return redirect("profile", phone=request.user.phone)