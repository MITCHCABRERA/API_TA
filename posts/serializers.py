from rest_framework import serializers
from .models import Post, Comment, User

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField()  # Accepts username as a string instead of a User object
    likes_count = serializers.IntegerField(source='total_likes', read_only=True)  # Fetches the total number of likes
    liked_by_user = serializers.SerializerMethodField()  # Determines if the current user has liked the post

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'privacy', 'likes_count', 'liked_by_user']

    def create(self, validated_data):
        """Overrides the default create method to convert the username into a User object before saving."""
        username = validated_data.pop('author')  # Extract the username from the request data
        try:
            user = User.objects.get(username=username)  # Fetch the User object from the database
        except User.DoesNotExist:
            raise serializers.ValidationError({"author": "User not found."})  # Raise an error if the user does not exist

        validated_data['author'] = user  # Replace the username with the actual User object
        return Post.objects.create(**validated_data)  # Create and return the Post instance

    def get_liked_by_user(self, obj):
        """Checks if the authenticated user has liked the post."""
        user = self.context.get('request').user if self.context.get('request') else None
        return user and user.is_authenticated and user in obj.likes.all()

    
    def get_author(self, obj):
        """Returns the author's username instead of their ID for better readability in API responses."""
        return obj.author.username if obj.author else None  # Ensures no error if the author field is null


        
        
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(write_only=True)  # Accepts username as input but doesn't return it in responses
    author_username = serializers.CharField(source='author.username', read_only=True)  # Outputs the author's username in responses

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'author_username', 'post', 'created_at']

    def create(self, validated_data):
        """Overrides the default create method to convert the username into a User object before saving."""
        username = validated_data.pop('author')  # Extract the username from the request data
        try:
            user = User.objects.get(username=username)  # Fetch the User object
        except User.DoesNotExist:
            raise serializers.ValidationError({"author": "User not found."})  # Raise an error if the user is not found

        validated_data['author'] = user  # Replace the username with the actual User object
        return Comment.objects.create(**validated_data)  # Create and return the Comment instance
