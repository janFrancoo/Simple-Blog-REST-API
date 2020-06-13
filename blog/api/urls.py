from django.urls import path, include
from blog.api import views
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    path('posts/', views.get_posts),
    path('posts/add', views.add_post),
    path('posts/<int:pk>', views.get_single_post),
    path('posts/<int:pk>/edit', views.update_post),
    path('posts/<int:pk>/delete', views.delete_post),
    path('posts/<int:pk>/like', views.like_post),
    path('posts/<int:pk>/unlike', views.unlike_post),
    path('login/', auth_views.obtain_auth_token),
]
