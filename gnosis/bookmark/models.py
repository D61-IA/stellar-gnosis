from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from catalog.models import Paper
from django.urls import reverse


# Create your models here.
# Bookmarks are private folders for user to store their findings so that they have fast access to them.
class Bookmark(models.Model):
    """A Bookmark model"""

    # Fields
    updated_at = models.DateField(null=True)
    created_at = models.DateField(auto_now_add=True, auto_now=False)

    paper = models.ForeignKey(to=Paper,
                              on_delete=models.CASCADE,
                              related_name="bookmarks")  # Paper.bookmarks()

    owner = models.ForeignKey(to=User,
                              on_delete=models.CASCADE,
                              related_name="bookmarks")  # User.bookmarks()

    # Methods
    def get_absolute_url(self):
        return reverse('bookmarks')

