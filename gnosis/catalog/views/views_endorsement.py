from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from catalog.models import Endorsement, Paper
from django.urls import reverse
from django.http import HttpResponseRedirect
#
# Endorsement views
#


@login_required
def endorsements(request):

    all_endorsements = Endorsement.objects.filter(user=request.user).order_by('-created_at')[:100]

    return render(request, "endorsement.html", {"endorsements": all_endorsements, })

@login_required
def endorsement_search(request):
    """Search for an endorsement"""
    endors = request.user.endorsements.all()
    results_message = ''
    if request.method == 'POST':
        keywords = request.POST.get("keywords", "")

        endors = endors.filter(paper__title__icontains=keywords)
        num_endors = len(endors)
        if endors:
            if num_endors > 25:
                results_message = f"Showing 25 out of {num_endors} paper endorsements found. For best results, please narrow your search."
                endors = endors[:25]
        else:
            results_message = "No results found. Please try again!"
    
    else:
        return HttpResponseRedirect(reverse("endorsements", ))
        
    return render(request, 'endorsement_results.html', {"endorsements": endors, "results_message": results_message})



@login_required
def endorsement_create(request, id):
    """Create an endorsement entry of a paper by the user, update the database"""
    user = request.user
    paper = get_object_or_404(Paper, pk=id)

    if request.method == "POST":
        e = Endorsement.objects.filter(paper=paper, user=user)
        response = {'endorsement': ""}

        if not e:
            print("Adding Endorsement.")
            e = Endorsement(user=user, paper=paper)
            e.save()
            response['result'] = "add"
        else:
            print("Endorsement deleted.")
            e.delete()
            response['result'] = "delete"

        return JsonResponse(response)

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def endorsement_delete(request, id):

    user = request.user
    paper = get_object_or_404(Paper, pk=id)
    e = Endorsement.objects.filter(user=user, paper=paper)

    if e:
        e.delete()

    return HttpResponseRedirect(reverse("endorsements"))
