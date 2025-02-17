from django.urls import path, include
from . import views 

from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import PostViewSet
from .views import CommentViewSet


# urlpatterns = [
#     path('users/', views.get_users, name='get_users'),
#     path('users/create/', views.create_user, name='create_user'),
#     path('posts/', views.get_posts, name='get_posts'),
#     path('posts/create/', views.create_post, name='create_post'),
# ]


router = DefaultRouter()
#router.register(r'users', UserViewSet, basename = 'user')
router.register(r'posts', PostViewSet, basename = 'post')
router.register(r'comments', CommentViewSet, basename = 'comment')

urlpatterns = [
    # Include the the routers URL
    path('', include(router.urls)),

    # User registration URL
    path ('register/', views.register, name = 'register')
]