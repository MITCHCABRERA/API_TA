"""
URL configuration for connectlyy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from oauth2_provider.views import TokenView

urlpatterns = [
    path('admin/', admin.site.urls),  # URL for accessing the Django admin panel

    path('api-auth/', include('rest_framework.urls')),  # Default login/logout views provided by Django REST Framework

    path('posts/', include('posts.urls')),  # Routes for handling posts, make sure `posts.urls` exists

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Endpoint to get an access and refresh token for JWT authentication

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Used to refresh the access token using a valid refresh token

    path('auth/', include('rest_framework_social_oauth2.urls')),  # OAuth2 authentication routes (ensure it’s correctly set up)

    path('o/token/', TokenView.as_view(), name='token'),  # Endpoint for handling OAuth2 token requests
]
