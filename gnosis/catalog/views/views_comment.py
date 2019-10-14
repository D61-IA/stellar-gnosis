from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from catalog.models import Paper, Comment
from catalog.views.utils.import_functions import *

from catalog.forms import CommentForm


from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db
from datetime import date
from nltk.corpus import stopwords
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from django.contrib import messages
# from catalog.views.views_codes import _code_find
import re


#
# Comment Views
#
@staff_member_required
def comments(request):
    """
    We should only show the list of comments if the user is admin. Otherwise, the user should
    be redirected to the home page.
    :param request:
    :return:
    """
    # Only superusers can view all the comments
    if request.user.is_superuser:
        all_comments = Comment.objects.all()
        return render(
            request,
            "comments.html",
            {"comments": all_comments, "num_comments": 0},
        )
    else:
        # other users are sent back to the paper index
        return HttpResponseRedirect(reverse("papers_index"))


@staff_member_required
def comment_detail(request, id):
    # Only superusers can view comment details.
    try:
        comment = Comment.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("papers_index")

    return render(request, "comment_detail.html", {"comment": comment})


@login_required
def comment_create(request):
    user = request.user

    # Retrieve paper using paper id
    paper_id = request.session["last-viewed-paper"]
    try:
        paper = Paper.objects.get(pk=paper_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("papers_index")

    if request.method == "POST":
        comment = Comment()
        comment.created_by = user
        comment.paper = paper
        form = CommentForm(instance=comment, data=request.POST)
        if form.is_valid():
            # add link from new comment to paper
            form.save()
            del request.session["last-viewed-paper"]
            return redirect("paper_detail", id=paper_id)
    else:  # GET
        form = CommentForm()

    return render(request, "comment_form.html", {"form": form})


@login_required
def comment_update(request, id):
    # retrieve paper by ID
    try:
        comment = Comment.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("papers_index"))

    if comment.created_by != request.user:
        return HttpResponseRedirect(reverse("papers_index"))

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment.text = form.cleaned_data["text"]
            comment.save()
            paper_id = request.session.get("last-viewed-paper", None)
            if paper_id:
                del request.session["last-viewed-paper"]
                return redirect("paper_detail", id=paper_id)
            else:
                return HttpResponseRedirect(reverse('comments_index'))
    # GET request
    else:
        form = CommentForm(
            initial={"text": comment.text, "publication_date": comment.created_at}
        )

    return render(request, "comment_update.html", {"form": form, "comment": comment})
