from django.contrib import admin
from catalog.models import Paper, Code, Comment, Person, Venue, Dataset
from catalog.models import ReadingGroup, ReadingGroupEntry
from catalog.models import Collection, CollectionEntry

# Register your models here.
admin.site.register(Paper)
admin.site.register(Dataset)
admin.site.register(Code)
admin.site.register(Comment)
admin.site.register(Person)
admin.site.register(Venue)
admin.site.register(ReadingGroup)
admin.site.register(ReadingGroupEntry)
admin.site.register(Collection)
admin.site.register(CollectionEntry)
