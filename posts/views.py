import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.http import JsonResponse
from posts.serializers import PostSerializer, CommentSerializer
from .models import Post, Comment
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.core.cache import cache  # ✅ Import cache

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admins to delete or modify posts/comments.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS (safe methods) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow modification if user is an admin
        return request.user.is_authenticated and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only owners (or admins) to edit/delete their own posts/comments.
    """
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, or OPTIONS (safe methods) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow modification if user is the owner or an admin
        return obj.author == request.user or request.user.is_staff

class CanViewPost(permissions.BasePermission):
    """
    Only allow viewing public posts or private posts if the user is the owner.
    """
    def has_object_permission(self, request, view, obj):
        if obj.privacy == 'public':
            return True
        
        # Only allow viewing private posts if the request user is the owner
        return obj.author == request.user

# User Registration View
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "We got ya in!",
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def news_feed(request):
    page_number = request.GET.get("page", "1")  # Get page number from query params

    # Debugging: Print the requested page number
    print(f"Requested Page: {page_number}")

    posts = Post.objects.all().order_by('-created_at')  # Get all posts

    paginator = PageNumberPagination()
    paginator.page_size = 10  # Set the page size

    try:
        paginated_posts = paginator.paginate_queryset(posts, request)  # Apply pagination
    except Exception as e:
        return Response({"detail": f"Pagination Error: {str(e)}"}, status=400)

    if not paginated_posts:  # If the page is empty, return a better message
        return Response({"detail": "No more pages available."}, status=400)

    serializer = PostSerializer(paginated_posts, many=True)
    return paginator.get_paginated_response(serializer.data)

# Get Users View
@api_view(['GET'])
def get_users(request):
    try:
        users = list(User.objects.values('id', 'username', 'email', 'date_joined'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Create User View
@api_view(['POST'])
def create_user(request):
    try:
        data = request.data
        user = User.objects.create(username=data['username'], email=data['email'])
        return JsonResponse({'id': user.id, 'message': 'Look at you, all signed up and ready to slay! 🔥'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Get Posts View
@api_view(['GET'])
def get_posts(request):
    try:
        posts = list(Post.objects.values('id', 'content', 'author_id', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # Debugging Line
            
            author = User.objects.get(id=int(data['author']))
            
            post = Post.objects.create(content=data['content'], author=author)
            return JsonResponse({'message': 'Post created successfully! ✅'}, status=201)
        
        except User.DoesNotExist:
            return JsonResponse({'error': f"User with ID {data.get('author')} not found!"}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
@api_view(['POST'])
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user  # Ensure this is an actual User instance

    if not isinstance(user, User):  # Debugging check
        return JsonResponse({"error": "Invalid user instance"}, status=400)

    post.likes.add(user)  # Make sure 'likes' is a ManyToManyField with User
    return JsonResponse({"message": "Post liked successfully"})
    """
    Allows an authenticated user to like a specific post.
    - The user is identified from `request.user`.
    - Ensures that `request.user` is a valid instance of the User model.
    - The `likes` field is assumed to be a ManyToManyField in the Post model.
    - If the user successfully likes the post, a success message is returned.
    """

@api_view(['POST'])
def unlike(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not post.likes.filter(id=request.user.id).exists():
        return JsonResponse({'message': 'You have not liked this post yet!'}, status=400)

    post.likes.remove(request.user)
    return JsonResponse({'message': 'Unliked successfully!', 'likes_count': post.likes.count()}, status=200)
    """
    Allows an authenticated user to unlike (remove like from) a specific post.
    - Ensures the post exists; otherwise, returns a 404 response.
    - Checks if the user has already liked the post before attempting to remove the like.
    - Removes the like and returns a success response along with the updated like count.
    """

# Home View
def home(request):
    return HttpResponse("こんにちは！")

# PostViewSet
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Post created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Post updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        post = self.get_object()
    
        if not request.user.is_authenticated:
         return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
         user = User.objects.get(id=request.user.id)  # Ensure the user instance
        except User.DoesNotExist:
         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if post.likes.filter(id=user.id).exists():
         return Response({"message": "You already liked this post!"}, status=status.HTTP_400_BAD_REQUEST)

        post.likes.add(user)
        return Response({"message": "Post liked!", "likes_count": post.likes.count()}, status=status.HTTP_200_OK)




    @action(detail=True, methods=['POST'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = User.objects.get(pk=request.user.pk)  # Ensure proper User instance

        if user not in post.likes.all():
            return Response({"message": "You haven't liked this post yet!"}, status=status.HTTP_400_BAD_REQUEST)

        post.likes.remove(user)
        return Response({"message": "Post unliked!", "likes_count": post.likes.count()}, status=status.HTTP_200_OK)

# CommentViewSet
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Comment created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Comment updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.completed:
            return Response({"error": "Cannot delete the Comment"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
