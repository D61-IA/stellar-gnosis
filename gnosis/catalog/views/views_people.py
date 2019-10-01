from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from catalog.models import Person, Paper
from catalog.forms import PersonForm
from catalog.forms import SearchPeopleForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db
from django.shortcuts import redirect
from django.contrib import messages


def _person_find(person_name, exact_match=False):
    """
    Searches the DB for a person whose name matches the given name
    :param person_name:
    :return:
    """
    person_name = person_name.lower()
    person_name_tokens = [w for w in person_name.split()]
    if exact_match:
        if len(person_name_tokens) > 2:
            query = "MATCH (p:Person) WHERE  LOWER(p.last_name) IN { person_tokens } AND LOWER(p.first_name) IN { person_tokens } AND LOWER(p.middle_name) IN { person_tokens } RETURN p LIMIT 20"
        else:
            query = "MATCH (p:Person) WHERE  LOWER(p.last_name) IN { person_tokens } AND LOWER(p.first_name) IN { person_tokens } RETURN p LIMIT 20"
    else:
        query = "MATCH (p:Person) WHERE  LOWER(p.last_name) IN { person_tokens } OR LOWER(p.first_name) IN { person_tokens } OR LOWER(p.middle_name) IN { person_tokens } RETURN p LIMIT 20"

    results, meta = db.cypher_query(query, dict(person_tokens=person_name_tokens))

    if len(results) > 0:
        print("Found {} matching people".format(len(results)))
        people = [Person.inflate(row[0]) for row in results]
        return people
    else:
        return None


def person_find(request):
    """
    Searching for a person in the DB.

    :param request:
    :return:
    """
    print("Calling person_find")
    people_found_ids = []
    message = None
    storage = messages.get_messages(request=request)
    for request_message in storage:
        people_found_ids = request_message.message
        print("IDs of people found: {}".format(people_found_ids))
        people_found_ids = people_found_ids.split(",")
        break

    people = []
    if len(people_found_ids) > 0:
        people = Person.nodes.filter(uid__in=people_found_ids)
        print("Retrieved {} people from the database".format(len(people)))

    if request.method == "POST":
        form = SearchPeopleForm(request.POST)
        print("Received POST request")
        if form.is_valid():

            people = _person_find(form.cleaned_data["person_name"])
            if people is not None:
                return render(request, "person_find.html", {"people": people, "form": form, "message": message})
            else:
                message = "No results found. Please try again!"

    elif request.method == "GET":
        print("Received GET request")
        form = SearchPeopleForm()

    return render(request, "person_find.html", {"people": people, "form": form, "message": message})

#
# Person Views
#
def persons(request):
    people = Person.nodes.order_by("-created")[:50]
    message = None
    if request.method == "POST":
        form = SearchPeopleForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            print("Valid form")
            people_found = _person_find(form.cleaned_data["person_name"])
            if people_found is not None:
                #print("Found people. Rendering person_find.html")
                people_found_ids = [person.uid for person in people_found]
                #print("ids as string {}".format(",".join(str(pid) for pid in people_found_ids)))
                messages.add_message(request, messages.INFO, ",".join(str(pid) for pid in people_found_ids))
                return redirect("person_find")
                # return render(
                #      request,
                #      "person_find.html",
                #      {"people": people_found, "form": form, "message": ""},
                # )
            else:
                message = "No results found. Please try again!"

    elif request.method == "GET":
        print("Received GET request")
        form = SearchPeopleForm()

    return render(
        request, "people.html", {"people": people, "form": form, "message": message}
    )


def person_detail(request, id):
    # Retrieve the paper from the database
    papers_authored = []
    query = "MATCH (a:Person) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        # There should be only one results because ID should be unique. Here we check that at
        # least one result has been returned and take the first result as the correct match.
        # Now, it should not happen that len(results) > 1 since IDs are meant to be unique.
        # For the MVP we are going to ignore the latter case and just continue but ultimately,
        # we should be checking for > 1 and failing gracefully.
        all_people = [Person.inflate(row[0]) for row in results]
        person = all_people[0]
    else:  # go back to the paper index page
        return render(
            request,
            "people.html",
            {"people": Person.nodes.all(), "num_people": len(Person.nodes.all())},
        )

    #
    # Retrieve all papers co-authored by this person and list them
    #
    query = "MATCH (a:Person)-[r:authors]->(p:Paper) where id(a)={id} return p"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        papers_authored = [Paper.inflate(row[0]) for row in results]
        print("Number of papers co-authored by {}: {}".format(person.last_name, len(papers_authored)))
        for p in papers_authored:
            print("Title: {}".format(p.title))
    else:
        print("No papers found for author {}".format(person.last_name))

    request.session["last-viewed-person"] = id
    return render(request, "person_detail.html", {"person": person, "papers": papers_authored})


@login_required
def person_create(request):
    user = request.user

    if request.method == "POST":
        person = Person()
        person.created_by = user.id
        form = PersonForm(instance=person, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("persons_index"))
    else:  # GET
        form = PersonForm()

    return render(request, "person_form.html", {"form": form})


@login_required
def person_update(request, id):
    # retrieve paper by ID
    # https://github.com/neo4j-contrib/neomodel/issues/199
    query = "MATCH (a:Person) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        all_people = [Person.inflate(row[0]) for row in results]
        person_inst = all_people[0]
    else:
        person_inst = Person()

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
        query = "MATCH (a:Person) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=id))
        if len(results) > 0:
            all_people = [Person.inflate(row[0]) for row in results]
            person_inst = all_people[0]
        else:
            person_inst = Person()
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


# should limit access to admin users only!!
@staff_member_required
def person_delete(request, id):
    print("WARNING: Deleting person id {} and all related edges".format(id))

    # Cypher query to delete the paper node
    query = "MATCH (p:Person) WHERE ID(p)={id} DETACH DELETE p"
    results, meta = db.cypher_query(query, dict(id=id))

    return HttpResponseRedirect(reverse("persons_index"))
