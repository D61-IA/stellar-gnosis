from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from catalog.models import Endorsement, Paper
from django.urls import reverse
from django.http import HttpResponseRedirect
#
# Endorsement views
#


@login_required
def endorsements(request):

    endorsement = request.user.endorsements.order_by('-created_at')

    return render(request, "endorsement.html", {"papers": endorsement, })


@login_required
def endorsement_create(request, id):
    """Create an endorsement entry of a paper by the user, update the database"""
    user = request.user
    paper = get_object_or_404(Paper, pk=id)

    if request.method == "POST":
        e = Endorsement.objects.filter(paper=paper).filter(user=user)
        if not e:
            endorsement_entry = Endorsement()
            endorsement_entry.user = user
            endorsement_entry.paper = paper
            endorsement_entry.save()

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def endorsement_undo(request, id):
    """Undo an endorsement of a paper, update both databases"""
    user = request.user
    paper = get_object_or_404(Paper, pk=id)

    if request.method == "POST":
        try:
            endorsement_entry = Endorsement.objects.filter(paper=paper, user=user)
            if endorsement_entry:
                endorsement_entry.delete()
        except:
            print("no such entry exists")
    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def endorsement_undo_from_view(request, id):
    """Undo an endorsement of a paper, update both databases"""
    user = request.user
    paper = get_object_or_404(Paper, pk=id)
    try:
        endorsement_entry = Endorsement.objects.filter(paper=paper, user=user)
        endorsement_entry.delete()
    except:
        print("Endorsment not found!")

    return HttpResponseRedirect(reverse("endorsements"))
