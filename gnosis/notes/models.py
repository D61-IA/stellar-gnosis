from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.CharField(max_length=100)
    text = models.TextField()
    date_posted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Private note on {self.paper} by {self.author.username}'