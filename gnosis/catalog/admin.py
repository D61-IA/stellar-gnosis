from django.contrib import admin
from django.http import HttpResponseRedirect

from catalog.models import ReadingGroup, ReadingGroupEntry
from catalog.models import Collection, CollectionEntry
from catalog.models import CommentFlag

from neomodel import db
from catalog.models import Comment

from django.urls import reverse
from catalog.models import EndorsementEntry

# Register your models here.
admin.site.register(ReadingGroup)
admin.site.register(ReadingGroupEntry)
admin.site.register(Collection)
admin.site.register(CollectionEntry)
admin.site.register(EndorsementEntry)


# def delete_selected(modeladmin, request, queryset):
#     for obj in queryset:
#         # delete selected flags
#         obj.delete()
#
#
# delete_selected.short_description = "Delete marked flags"


def delete_comment(modeladmin, request, queryset):
    for obj in queryset:
        query = "MATCH (a:Comment) WHERE ID(a)={id} DETACH DELETE a"
        results, meta = db.cypher_query(query, dict(id=obj.comment_id))

        # delete flags about the same comment
        CommentFlag.objects.filter(comment_id=obj.comment_id).delete()


delete_comment.short_description = "Delete marked COMMENTS and their flags"


def delete_flags(modeladmin, request, queryset):
    for obj in queryset:
        # delete flags about the same comment
        CommentFlag.objects.filter(comment_id=obj.comment_id).delete()


delete_flags.short_description = "Delete all FLAGS about the marked comments"


# define customized interface for flagged comment
class FlaggedCommentAdmin(admin.ModelAdmin):
    change_form_template = "admin/flag_changeform.html"
    list_display = ['violation', 'get_comment']
    ordering = ['comment_id', 'violation']
    actions = [delete_comment, delete_flags]

    readonly_fields = ('get_comment', 'created_at')

    def response_change(self, request, obj):
        if "_delete-comment" in request.POST:
            query = "MATCH (a:Comment) WHERE ID(a)={id} DETACH DELETE a"
            results, meta = db.cypher_query(query, dict(id=obj.comment_id))
            obj.delete()

            # delete flags about the same comment
            CommentFlag.objects.filter(comment_id=obj.comment_id).delete()
            return HttpResponseRedirect(reverse('admin:catalog_flaggedcomment_changelist'))

        if "_delete-flags" in request.POST:
            CommentFlag.objects.filter(comment_id=obj.comment_id).delete()
            return HttpResponseRedirect(reverse('admin:catalog_flaggedcomment_changelist'))

        return super().response_change(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def get_comment(self, obj):
        query = "MATCH (a:Comment) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=obj.comment_id))
        comment = None
        if len(results) > 0:
            all_comments = [Comment.inflate(row[0]) for row in results]
            comment = all_comments[0]

        return comment.text

    get_comment.short_description = 'Comment'


admin.site.register(CommentFlag, FlaggedCommentAdmin)
