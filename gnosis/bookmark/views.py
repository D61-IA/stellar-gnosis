from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Bookmark, BookmarkEntry
from django.urls import reverse
from django.http import HttpResponseRedirect
from nltk.corpus import stopwords


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

@login_required
def search_bookmarks(request):
        keyword = request.POST.get('keyword1', "")
        # pre-process query
        english_stopwords = stopwords.words('english')
        if len(keyword)>1:
            search_keywords_tokens = [w for w in keyword.split(' ') if w not in english_stopwords]
        else:
            search_keywords_tokens = [keyword]
        bookmark = Bookmark.objects.filter(owner=request.user)[0]
        print("  ==> bookmark found")
        # rank the query results
        match_count = {}
        for paper in range(len(bookmark.papers.all())):
            match_count[paper] = 0
            for token in search_keywords_tokens:
                if token.lower() in bookmark.papers.all()[paper].paper_title.lower():
                    match_count[paper] += 1
        pairs = [(i,j) for (j,i) in match_count.items() if not i == 0]
        pairs.sort()
        papers = [bookmark.papers.all()[i] for (j,i) in pairs]
        # If no input query, display all papers
        if not search_keywords_tokens:
            papers = bookmark.papers
        return render(request,
                        "bookmark.html",
                      {
                          "papers": papers,
                      }
                      )
