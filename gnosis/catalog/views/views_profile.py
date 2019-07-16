from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from catalog.models import UserProfile
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


@login_required
def user_profile(request):

    # user = get_object_or_404(User, pk=id)

    return render(request, "user_profile.html", {})
