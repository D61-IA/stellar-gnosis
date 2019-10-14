from django.contrib import admin
from catalog.models import Paper, Code, Comment
from catalog.models import ReadingGroup, ReadingGroupEntry
from catalog.models import Collection, CollectionEntry

# Register your models here.
admin.site.register(Paper)
admin.site.register(Code)
admin.site.register(Comment)
admin.site.register(ReadingGroup)
admin.site.register(ReadingGroupEntry)
admin.site.register(Collection)
admin.site.register(CollectionEntry)
