from django.urls import path
from .views import (
    accept_friend_request, 
    send_friend_request, 
    all_users, 
    signupview,
    loginview,
    home,
    logout_view,
    friend_request,
    friends,
    create_post,
    update_post,
    post_list,
    post_detail,
    post_delete,
    profile_page,
    user_search
)

urlpatterns = [
    path('search/', user_search, name='search'),
    path("user/<phone>/", profile_page,name="profile"),
    path("logout/", logout_view, name="logout"),
    path("new/", create_post, name="create_post"),
    path("update/<slug>", update_post, name="update_post"),
    path('delete/<str:slug>', post_delete.as_view(), name="post_delete"),
    path("", home, name="home"),
    path("", post_list, name="post_list"),
    path("friends/", friends, name="friends"),
    path("login/",loginview, name="login"),
    path("signup/", signupview, name="signup"),
    path("all_users/", all_users, name="users"),
    path("friend_requests/", friend_request, name="friend_request"),
    path('send_friend_request/<int:userId>/', send_friend_request, name="send_friend_request"),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/' , post_detail,  name="post_detail"),
    path('accept_friend_request/<int:requestID>/', accept_friend_request, name="accept_friend_request"),
]