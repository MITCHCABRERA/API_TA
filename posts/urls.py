from django.urls import path, include
from . import views 

from rest_framework.routers import DefaultRouter

from .views import PostViewSet, create_post, like, news_feed, unlike
from .views import CommentViewSet
from rest_framework.authtoken.views import obtain_auth_token

# urlpatterns = [
#     path('users/', views.get_users, name='get_users'),
#     path('users/create/', views.create_user, name='create_user'),
#     path('posts/', views.get_posts, name='get_posts'),
#     path('posts/create/', views.create_post, name='create_post'),
#     path('posts/<int:post_id>/like/', like, name='like-post'),  # Like a specific post
#     path('posts/<int:post_id>/unlike/', unlike, name='unlike-post'),  # Unlike a specific post
# ]

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),  # Includes all registered viewset routes

    # User authentication & registration
    path('register/', views.register, name='register'),  # User registration endpoint
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # Token authentication endpoint
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),  # OAuth authentication

    # Post-related endpoints
    path('create_post/', create_post, name='create_post'),  # Create a new post
    path('feed/', news_feed, name='news-feed'),  # News feed (paginated posts)
]