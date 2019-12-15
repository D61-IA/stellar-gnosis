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
            user.profile.about = form.clean_about()
            user.profile.affiliation = form.clean_affiliation()
            user.profile.interests = form.clean_interests()
            user.profile.job = form.clean_job()
            user.profile.city = form.clean_city()
            user.profile.country = form.clean_country()
            user.profile.website = form.clean_website()
            user.profile.twitter = form.clean_twitter()
            user.profile.github = form.clean_github()
            user.profile.linkedin = form.clean_linkedin()
            user.save()
            return HttpResponseRedirect(reverse("profile", kwargs={"id": user.id}))
    # GET request
    else:
        form = ProfileForm(
            initial={
                "about": user.profile.about,
                "affiliation": user.profile.affiliation,
                "job": user.profile.job,
                "city": user.profile.city,
                "country": user.profile.country,
                "interests": user.profile.interests,
                "website": user.profile.website,
                "twitter": user.profile.twitter,
                "github": user.profile.github,
                "linkedin": user.profile.linkedin
            }
        )

    return render(request, "profile_update.html", {"form": form })
