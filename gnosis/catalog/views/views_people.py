from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from catalog.models import Person, Paper
from django.shortcuts import render
from catalog.forms import PersonForm
from catalog.forms import SearchPeopleForm
from catalog.views.utils.import_functions import *

from django.urls import reverse
from django.http import HttpResponseRedirect


#
# Person Views
#
def persons(request):
    people = Person.objects.order_by("-created_at")[:100]  # nodes.order_by("-created")[:50]
    message = None

    if request.method == 'POST':
        form = SearchPeopleForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            print("Valid form")
            people_found = None  # _person_find(form.cleaned_data["person_name"])
            query = form.cleaned_data["person_name"].lower()
            print(f"Searching for people using keywords {query}")
            people = Person.objects.annotate(
                 search=SearchVector('first_name', 'last_name', 'middle_name')
            ).filter(search=SearchQuery(query, search_type='plain'))

            print(people)

            if people is None:
                message = "No results found. Please try again!"

    elif request.method == "GET":
        print("Received GET request")
        form = SearchPeopleForm()

    return render(
        request, "people.html", {"people": people, "form": form, "message": message}
    )


def person_detail(request, id):
    # Retrieve the paper from the database
    try:
        person = Person.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("persons_index"))

    papers_authored = person.papers.all()

    request.session["last-viewed-person"] = id
    return render(request, "person_detail.html", {"person": person, "papers": papers_authored})


@login_required
@staff_member_required
def person_create(request):

    if request.method == "POST":
        person = Person()
        person.created_by = request.user
        form = PersonForm(instance=person, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("persons_index"))
    else:  # GET
        form = PersonForm()

    return render(request, "person_form.html", {"form": form})


@login_required
@staff_member_required
def person_update(request, id):

    try:
        person_inst = Person.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("persons_index"))

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person_inst.first_name = form.cleaned_data["first_name"]
            person_inst.middle_name = form.cleaned_data["middle_name"]
            person_inst.last_name = form.cleaned_data["last_name"]
            person_inst.affiliation = form.cleaned_data["affiliation"]
            person_inst.website = form.cleaned_data["website"]
            person_inst.save()

            return HttpResponseRedirect(reverse("persons_index"))
    # GET request
    else:
        form = PersonForm(
            initial={
                "first_name": person_inst.first_name,
                "middle_name": person_inst.middle_name,
                "last_name": person_inst.last_name,
                "affiliation": person_inst.affiliation,
                "website": person_inst.website,
            }
        )

    return render(request, "person_update.html", {"form": form, "person": person_inst})


# access limited to admin users only!!
@staff_member_required
def person_delete(request, id):

    try:
        person = Person.objects.get(pk=id)
        person.delete()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("persons_index"))

    return HttpResponseRedirect(reverse("persons_index"))
