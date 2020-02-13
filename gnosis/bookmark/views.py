from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Bookmark
from django.urls import reverse
from django.http import HttpResponseRedirect

@login_required
def bookmarks(request):
    all_bookmarks = Bookmark.objects.filter(owner=request.user)

    return render(request, "bookmarks.html", {"bookmarks": all_bookmarks, 'type': 'bookmark'})


@login_required
def bookmark_delete(request, id):
    """Delete view"""
    print("WARNING: Deleting bookmark entry with pid {}".format(id))

    bookmark = get_object_or_404(Bookmark, pk=id)

    if bookmark.owner == request.user:
        bookmark.delete()

    return HttpResponseRedirect(reverse("bookmarks"))


@login_required
def bookmark_search(request):
    """Search for a bookmark by its title"""
    keywords = request.GET.get('keywords','').strip()

    if keywords == '':
        bms = Bookmark.objects.filter(owner=request.user)
    else:
        bms = request.user.bookmarks.filter(paper__title__icontains=keywords)

    return render(request, "bookmarks.html", {"bookmarks": bms, 'type': 'bookmark'})
