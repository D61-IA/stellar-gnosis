from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Bookmark
from django.urls import reverse
from django.http import HttpResponseRedirect

@login_required
def bookmarks(request):
    all_bookmarks = Bookmark.objects.filter(owner=request.user)

    return render(request, "bookmarks.html", {"bookmarks": all_bookmarks})


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
    keywords = request.GET.get('keywords','')

<<<<<<< HEAD
    bms = request.user.bookmarks.filter(paper__title__icontains=keywords)

    return render(request, "bookmarks.html", {"bookmarks": bms})
=======
    bms = request.user.bookmarks.all()
    results_message = ''
    if request.method == 'POST':
        keywords = request.POST.get("keywords", "")

        bms = bms.filter(paper__title__icontains=keywords)
        num_bms = len(bms)
        if bms:
            if num_bms > 25:
                results_message = f"Showing 25 out of {num_bms} bookmarks found. For best results, please narrow your search."
                bms = bms[:25]
        else:
            results_message = "No results found. Please try again!"
    else:
        return HttpResponseRedirect(reverse("bookmarks", ))

    return render(request, "bookmark_results.html", {"bookmarks": bms, "results_message": results_message,})
>>>>>>> 48047f8ce18133db09ebb26167b7bdbdf32b6d92
