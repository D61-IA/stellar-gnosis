from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Bookmark, BookmarkEntry
from django.urls import reverse
from django.http import HttpResponseRedirect


@login_required
def bookmark(request):

    bookmark = Bookmark.objects.filter(owner = request.user)

    if not bookmark:
        user_bookmark = Bookmark()
        user_bookmark.owner = request.user
        user_bookmark.save()
    else:
        user_bookmark = bookmark[0]

    if user_bookmark.owner == request.user:
        papers = user_bookmark.papers.order_by('-created_at')

        return render(request, "bookmark.html", {"bookmark": user_bookmark,
                                                            "papers": papers, })

    return HttpResponseRedirect(reverse("bookmark"))




@login_required
def bookmark_entry_remove(request, pid):
    """Delete view"""
    print("WARNING: Deleting bookmark entry with pid {}".format(pid))

    # check if the bookmark for the user exists, delete the entry
    try:
        bookmark = Bookmark.objects.filter(owner = request.user)[0]
        print("  ==> bookmark found")
        b_entry = bookmark.papers.filter(paper_id=pid)[0]
        print("   ==> entry found")
        b_entry.delete()
    except:
        return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": pid, }))

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": pid, }))

@login_required
def bookmark_entry_remove_from_view(request, pid):
    """Delete view"""
    print("WARNING: Deleting bookmark entry with pid {}".format(pid))

    # check if the bookmark for the user exists
    try:
        bookmark = Bookmark.objects.filter(owner = request.user)[0]
        print("  ==> bookmark found")
        b_entry = bookmark.papers.filter(paper_id=pid)[0]
        print("   ==> entry found")
        b_entry.delete()
    except:
        return HttpResponseRedirect(reverse("bookmarks"))

    return HttpResponseRedirect(reverse("bookmarks"))
