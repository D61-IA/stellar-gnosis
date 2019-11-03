from django.db import models
from django.contrib.auth.models import User
from catalog.models import Paper


class Note(models.Model):

    note_content = models.TextField()  # The note content

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who create the note
    paper = models.ForeignKey(Paper,
                              on_delete=models.CASCADE,  # deleting a paper deletes all associated comments
                              )

    # paper_id = models.IntegerField(null=False, blank=False)  # A paper in the Neo4j DB
    created_at = models.DateTimeField()  # The first time the note was created
    updated_at = models.DateTimeField(auto_now=True)  # The last time the note was modified

    def __str__(self):
        return "Private note on paper" + str(self.paper_id) + " by " + str(self.created_by.username)

    class Meta:
        ordering = ['-updated_at']
