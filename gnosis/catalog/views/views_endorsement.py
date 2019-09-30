from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from catalog.models import EndorsementEntry
from django.urls import reverse
from django.http import HttpResponseRedirect
from catalog.views.views import _get_paper_by_id
from datetime import date
#
# Endorsement views
#

@login_required
def endorsements(request):

    endorsement = request.user.endorsements.order_by('-created_at')

    return render(request, "endorsement.html", {"papers": endorsement, })



@login_required
def endorsement_create(request, paper_id):
    """Create an endorsement entry of a paper by the user, update the database"""
    user = request.user

    if request.method == "POST":
        e = EndorsementEntry.objects.filter(paper_id = paper_id).filter(user = user)
        if not e:
            endorsement_entry = EndorsementEntry()
            endorsement_entry.user = user
            endorsement_entry.paper_id = paper_id
            endorsement_entry.paper_title = _get_paper_by_id(paper_id).title
            endorsement_entry.save()

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": paper_id}))


@login_required
def endorsement_undo(request, paper_id):
    """Undo an endorsement of a paper, update both databases"""
    user = request.user
    if request.method == "POST":
        try:
            endorsement_entry = EndorsementEntry.objects.filter(paper_id=paper_id, user=user)[0]
            endorsement_entry.delete()
        except:
            print("no such entry exists")
        return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": paper_id}))

    return render(request, "paper_detail.html")

@login_required
def endorsement_undo_from_view(request, paper_id):
    """Undo an endorsement of a paper, update both databases"""
    user = request.user
    try:
        endorsement_entry = EndorsementEntry.objects.filter(paper_id=paper_id, user=user)[0]
        endorsement_entry.delete()
        message = None
    except:
        message = "no such entry exists"
    return HttpResponseRedirect(reverse("endorsements"))
