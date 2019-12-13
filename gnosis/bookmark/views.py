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
def search_bookmarks(request):
    keywords = request.POST.get("keywords", "")
    # pre-process query
    #english_stopwords = stopwords.words("english")
    #if len(keyword) > 1:
    #    search_keywords_tokens = [
    #        w for w in keyword.split(" ") if w not in english_stopwords
    #    ]
    #else:
    #    search_keywords_tokens = [keyword]
    bookmark = Bookmark.objects.filter(owner=request.user)[0]
    print("  ==> bookmark found")
    # rank the query results
    match_count = {}
    for paper in range(len(bookmark.papers.all())):
        match_count[paper] = 0
        for token in search_keywords_tokens:
            if token.lower() in bookmark.papers.all()[paper].paper_title.lower():
                match_count[paper] += 1
    pairs = [(i, j) for (j, i) in match_count.items() if not i == 0]
    pairs.sort()
    papers = [bookmark.papers.all()[i] for (j, i) in pairs]
    # If no input query, display all papers
    if not search_keywords_tokens:
        papers = bookmark.papers
    return render(request, "bookmark.html", {"papers": papers})
