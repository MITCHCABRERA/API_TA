from django.db import models

# Create your models here.

class User (models.Model):
    #my user's uniq username, email, and timestamp when acc was made
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
    
class Post (models.Model):
    # text field of the app! + Author(user)'s name & TIMESTAMP OFC
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.content[:50]
        return f"Post by {self.author.username} at {self.created_at}"
    #f means format

    
    
    
class Comment (models.Model):
    text = models.TextField()
#    author = models.ForeignKey(User, related_name= 'comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
    
    
    
    
     
        """👀 What it’s doing:
        
            Basically, when you ask Python to show your object 
            (like when you print it or see it in the admin panel), 
            this function is like:
                "Hold up, I got you, but we ain't spilling everything!" 💅

            Instead of showing the whole content, 
            it’s just serving you the first 50 characters, 
            like a cute lil' sneak peek. 📜✨
        """
        