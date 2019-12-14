from django.contrib import admin
from catalog.models import Paper, Code, Comment, Person, Venue, Dataset
from django.http import HttpResponseRedirect
from catalog.models import ReadingGroup, ReadingGroupEntry, ReadingGroupMember
from catalog.models import Collection, CollectionEntry, Endorsement
from catalog.models import CommentFlag
from catalog.models import PaperAuthorRelationshipData, PaperDatasetRelationshipData
from catalog.models import Profile

from catalog.models import Comment

from django.urls import reverse

# Register your models here.
admin.site.register(Paper)
admin.site.register(Dataset)
admin.site.register(Code)
admin.site.register(Comment)
admin.site.register(CommentFlag)
admin.site.register(Person)
admin.site.register(Venue)
admin.site.register(ReadingGroup)
admin.site.register(ReadingGroupEntry)
admin.site.register(ReadingGroupMember)
admin.site.register(Collection)
admin.site.register(CollectionEntry)
admin.site.register(Endorsement)
admin.site.register(PaperAuthorRelationshipData)
admin.site.register(PaperDatasetRelationshipData)
admin.site.register(Profile)
