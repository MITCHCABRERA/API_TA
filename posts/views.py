
""" 
render and JsonResponse 
are coming through from Django 
to handle views and JSON responses 
like a boss."""
# User model is imported to fetch data from the database. 📊
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view 
from rest_framework.response import Response
from rest_framework import viewsets, status

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from posts.serializers import PostSerializer, CommentSerializer
# from .models import User # Comment WE DONT NEED IT ANYMORE
from .models import Post
from .models import Comment
from django.http import HttpResponse

# Create your views here.

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create_user(username = username, password = password)
        
        return Response({"message": "We got ya in!"}, status=status.HTTP_201_CREATED)
                                
# This function is all about serving up user data when the app calls for it. 📞
def get_users(request):
    try:
        users = list(User.objects.values('id',
                                         'username', 
                                         'email',
                                         'created_at'))
        
        return JsonResponse(users, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(username=data['username'],email=data['email'])
            
            return JsonResponse ({'id': user.id, 
                                'message': 
                                'Look at you, all signed up and ready to slay! 🔥'}, status=201)
        except Exception as e:
            return JsonResponse({'Uh oh!': str(e)}, status=400)
        
        
def get_posts(request):
    try:
        posts = list(Post.objects. values('id',
                                         'content',
                                         'author',
                                         'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get (id=data['author'])
            post = Post.objects.create(content=data['content'], author=author)
            return JsonResponse({'message': 'Post created. Done and dusted! ✅'}, status=201)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Who? Where? This user vanished into thin air! Can’t find that user. Maybe sign up first? 😊'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        
def home(request):
    return HttpResponse("こんにちは！")


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)
        return Response({"message": " Post created successfully", "data": serializer.data}, status = status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data = request.data, partial = partial)
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        return Response({"message": " Post Updated successfully", "data": serializer.data}, status = status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.completed:
            return Response({"error": "Cannot delete the Post"}, status = status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({"message": " Post deleted successfully"}, status = status.HTTP_204_NO_CONTENT)
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)
        return Response({"message": " Comment created successfully", "data": serializer.data}, status = status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data = request.data, partial = partial)
        serializer.is_valid(raise_exception = True)
        self.perform_update(serializer)
        return Response({"message": " Comment Updated successfully", "data": serializer.data}, status = status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.completed:
            return Response({"error": "Cannot delete the Comment"}, status = status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({"message": " Comment deleted successfully"}, status = status.HTTP_204_NO_CONTENT)