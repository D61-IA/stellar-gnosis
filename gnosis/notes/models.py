from django.db import models
from django.contrib.auth.models import User
from catalog.models import Paper

class Note(models.Model):

    note_content = models.TextField()  # The note content
    created_at = models.DateField(auto_now_add=True, auto_now=False)  # The first time the note was created
    updated_at = models.DateField(auto_now=True, null=True)  # The last time the note was modified

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")  # The user who create the note
    paper = models.ForeignKey(to=Paper, on_delete=models.CASCADE, related_name="notes")  
 

    def __str__(self):
        return "Private note on paper" + str(self.paper) + " by " + str(self.created_by)

    class Meta:
        ordering = ['-updated_at']
