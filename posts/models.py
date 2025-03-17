from django.db import models

# Define available roles
ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('user', 'User'),
    ('guest', 'Guest'),
)

PRIVACY_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private'),
)

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')  # ✅ Role field added

    def __str__(self):
       return f"{self.username} ({self.role})"  # ✅ Shows role in string representation


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')  # ✅ Privacy field added


    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}: {self.content[:50]}"  # ✅ Returns username


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)  # ✅ Add back the author field
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}: {self.text[:50]}"  # ✅ Returns username
