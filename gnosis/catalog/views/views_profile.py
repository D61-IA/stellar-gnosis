from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from catalog.models import Profile
from catalog.forms import ProfileForm
from django.urls import reverse
from django.http import HttpResponseRedirect


@login_required
def profile_detail(request, id):
    # Retrieve the paper from the database
    user = get_object_or_404(User, pk=id)
    profile = user.profile

    # request.session["last-viewed-dataset"] = id
    return render(request, "profile_detail.html",  {"profile": profile})

@login_required
def profile_update(request):

    user = request.user

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.profile.bio = form.clean_bio()
            user.profile.affiliation = form.clean_affiliation()
            user.save()
            return HttpResponseRedirect(reverse("profile", kwargs={"id": user.id}))
    # GET request
    else:
        form = ProfileForm(
            initial={
                "bio": user.profile.bio,
                "affiliation": user.profile.affiliation,
                "job": user.profile.job,
                "interests": user.profile.interests,
                "website": user.profile.website,
            }
        )

    return render(request, "profile_update.html", {"form": form })
