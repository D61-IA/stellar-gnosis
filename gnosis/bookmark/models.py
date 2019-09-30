from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
# Bookmarks are private folders for user to store their findings so that they have fast access to them.
class Bookmark(models.Model):
    """A Bookmark model"""

    # Fields

    updated_at = models.DateField(null=True)

    owner = models.ForeignKey(to=User,
                              on_delete=models.CASCADE,
                              related_name="bookmarks")

    # Methods
    def get_absolute_url(self):
        return reverse('bookmark_detail', args=[str(self.id)])


class BookmarkEntry(models.Model):
    """An entry, that is paper or code."""

    # Fields
    bookmark = models.ForeignKey(to=Bookmark,
                                   on_delete=models.CASCADE,
                                   related_name="papers")  # Bookmark.papers()

    paper_id = models.IntegerField(null=False, blank=False)  # A paper in the Neo4j DB
    paper_title = models.TextField(null=False, blank=False)  # The paper title to avoid extra DB calls

    created_at = models.DateField(auto_now_add=True, auto_now=False)

    def get_absolute_url(self):
        return reverse('bookmark_detail', args=[str(self.id)])

    def __str__(self):
        return str(self.paper_id)
