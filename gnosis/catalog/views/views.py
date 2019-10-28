from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from catalog.models import Paper, PaperRelationshipType, Person, Dataset, Venue, Comment, Code
from catalog.models import ReadingGroup, ReadingGroupEntry
from catalog.models import Collection, CollectionEntry
from catalog.views.utils.import_functions import *

from catalog.forms import (
    PaperForm,
    DatasetForm,
    VenueForm,
    CommentForm,
    PaperImportForm,
)
from catalog.forms import (
    SearchVenuesForm,
    SearchPapersForm,
    SearchPeopleForm,
    SearchDatasetsForm,
    SearchCodesForm,
    PaperConnectionForm,
)
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from django.contrib import messages
import re


#
# Paper Views
def papers(request):
    # Retrieve the papers ordered by newest addition to DB first.
    # limit to maximum 50 papers until we get pagination to work.
    # However, even with pagination, we are going to want to limit
    # the number of papers retrieved for speed, especially when the
    # the DB grows large.
    all_papers = Paper.objects.all()  # nodes.order_by("-created")[:50]

    message = None
    if request.method == "POST":
        form = SearchPapersForm(request.POST)
        print("papers: Received POST request")
        if form.is_valid():
            paper_title = form.cleaned_data["paper_title"].lower()
            print(f"Searching for paper using keywords {paper_title}")
            papers = Paper.objects.annotate(
                 search=SearchVector('title')
            ).filter(search=SearchQuery(paper_title, search_type='plain'))

            print(papers)

            if papers:
                return render(request, "paper_results.html", {"papers": papers, "form": form, "message": ""})
            else:
                message = "No results found. Please try again!"

    elif request.method == "GET":
        print("papers: Received GET request")
        form = SearchPapersForm()

    return render(
        request,
        "papers.html",
        {
            "papers": all_papers,
            "form": form,
            "message": message,
        },
    )


def paper_authors(request, id):
    """Displays the list of authors associated with this paper"""
    relationship_ids = []
    try:
        paper = Paper.objects.get(pk=id)
        authors = paper.person_set.all()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse(("papers_index")))

    print("Retrieved paper with title {}".format(paper.title))

    num_authors = authors.count()  # len(authors)
    print("paper author link ids {}".format(relationship_ids))
    print("Found {} authors for paper with id {}".format(len(authors), id))
    # for rid in relationship_ids:
    delete_urls = [
        reverse("paper_remove_author", kwargs={"id": id, "rid": author.id})
        for author in authors  # relationship_ids
    ]
    print("author remove urls")
    print(delete_urls)

    authors = zip(authors, delete_urls)

    return render(request, "paper_authors.html", {"authors": authors, "paper": paper, "number_of_authors": num_authors})


# should limit access to admin users only!!
@staff_member_required
def paper_remove_author(request, id, rid):
    print("Paper id {} and author id {}".format(id, rid))

    try:
        paper = Paper.objects.get(pk=id)
        author = Person.objects.get(pk=rid)
        author.papers.remove(paper)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("paper_authors", kwargs={"id": id}))
    # TO DO
    # What does this return? How can I make certain that the paper was deleted?

    return HttpResponseRedirect(reverse("paper_authors", kwargs={"id": id}))


# should limit access to admin users only!!
@staff_member_required
def paper_delete(request, id):
    print("WARNING: Deleting paper id {} and all related edges".format(id))

    try:
        paper = Paper.objects.filter(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("papers_index"))

    paper.delete()

    return HttpResponseRedirect(reverse("papers_index"))


def paper_detail(request, id):
    # Retrieve the paper from the database
    paper = get_object_or_404(Paper, pk=id)

    print(f"Paper 'from' relationships {paper.papers.all()}")
    for paper_to in paper.papers.all():
        rel_model = PaperRelationshipType.objects.get(paper_from=paper, paper_to=paper_to)
        print(f"{rel_model.relationship_type}")

    # Retrieve the paper's authors
    # authors is a list of strings so just concatenate the strings.
    # ToDo: Improve this code to correctly handle middle names that are more than one word.
    authors_set = paper.person_set.all()
    authors = []
    for author in authors_set:
        author_name = str(author)  # author.first_name[0]+'. '+author.middle_name
        author_name = author_name.split()
        if len(author_name) > 2:
            authors.append(author_name[0][0]+'. '+author_name[1][0]+'. '+author_name[2])
        else:
            authors.append(author_name[0][0]+'. '+author_name[1])
    authors = ', '.join(authors)

    comments = paper.comment_set.all()
    codes = paper.code_set.all()
    datasets = paper.dataset_set.all()
    print(datasets)
    venue = paper.was_published_at

    request.session["last-viewed-paper"] = id

    ego_network_json = []  #_get_node_ego_network(paper.id, paper.title)

    # print("ego_network_json: {}".format(ego_network_json))
    return render(
        request,
        "paper_detail.html",
        {
            "paper": paper,
            "venue": venue,
            "authors": authors,
            "comments": comments,
            "codes": codes,
            "datasets": datasets,
            "num_comments": comments.count(),
            "ego_network": ego_network_json,
        },
    )


# def _get_node_ego_network(id, paper_title):
#     """
#     Returns a json formatted string of the nodes ego network
#     :param id:
#     :return:
#     """
#     # query for everything that points to the paper
#     query_all_in = "MATCH (s:Paper {title: {paper_title}}) <-[relationship_type]- (p) RETURN p, " \
#                    "Type(relationship_type) "
#
#     # query for everything the paper points to
#     query_all_out = "MATCH (s:Paper {title: {paper_title}}) -[relationship_type]-> (p) RETURN p, " \
#                     "Type(relationship_type) "
#
#     results_all_in, meta = db.cypher_query(query_all_in, dict(paper_title=paper_title))
#
#     results_all_out, meta = db.cypher_query(query_all_out, dict(paper_title=paper_title))
#
#     print("Results out are: ", results_all_out)
#
#     print("Results in are: ", results_all_in)
#
#     ego_json = "{{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}'}} }}".format(
#         id, paper_title, reverse("paper_detail", kwargs={"id": id}), 'Paper', 'origin'
#     )
#
#     node_temp = ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"
#     rela_temp = ",{{data: {{ id: '{}{}{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"
#
#     # Assort nodes and store them in arrays accordingly
#     # 'out' refers to being from the paper to the object
#     if len(results_all_out) > 0:
#         # line property for out
#         line = "solid"
#
#         for row in results_all_out:
#             new_rela = row[1].replace("_", " ")
#
#             for label in row[0].labels:
#
#                 if label == 'Paper':
#                     tp = Paper.inflate(row[0])
#
#                     # adding paper node
#                     ego_json += node_temp.format(
#                         tp.id, tp.title, reverse("paper_detail", kwargs={"id": tp.id}), 'Paper', new_rela
#                     )
#
#                     # adding relationship with paper node
#                     ego_json += rela_temp.format(
#                         id, '-', tp.id, new_rela, id, tp.id, line
#                     )
#
#                 if label == 'Person':
#                     tpe = Person.inflate(row[0])
#                     middleName = ''
#                     # reformat middle name from string "['mn1', 'mn2', ...]" to array ['mn1', 'mn2', ...]
#                     if tpe.middle_name is not None:
#                         middleNames = tpe.middle_name[1:-1].split(', ')
#                         print(middleNames)
#                         # concatenate middle names to get 'mn1 mn2 ...'
#                         for i in range(len(middleNames)):
#                             middleName = middleName + " " + middleNames[i][1:-1]
#
#                     # When middle names have "'", like 'D'Angelo'
#                     middleName = middleName.replace("'", r"\'")
#
#                     ego_json += ", {{data : {{id: '{}', first_name: '{}', middle_name: '{}', last_name: '{}', href: '{}', " \
#                                 "type: '{}', " \
#                                 "label: '{}'}} }}".format(
#                         tpe.id, tpe.first_name, middleName, tpe.last_name,
#                         reverse("person_detail", kwargs={"id": tpe.id}), 'Person', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         id, "-", tpe.id, new_rela, id, tpe.id, line
#                     )
#
#                 if label == 'Venue':
#                     tv = Venue.inflate(row[0])
#
#                     ego_json += node_temp.format(
#                         tv.id, tv.name, reverse("venue_detail", kwargs={"id": tv.id}), 'Venue', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         id, '-', tv.id, new_rela, id, tv.id, line
#                     )
#
#                 if label == 'Dataset':
#                     td = Dataset.inflate(row[0])
#                     ego_json += node_temp.format(
#                         td.id, td.name, reverse("dataset_detail", kwargs={"id": td.id}), 'Dataset', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         id, '-', td.id, new_rela, id, td.id, line
#                     )
#
#                 if label == 'Code':
#                     tc = Code.inflate(row[0])
#                     ego_json += node_temp.format(
#                         tc.id, 'Code', reverse("code_detail", kwargs={"id": tc.id}), 'Code', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         id, '-', tc.id, new_rela, id, tc.id, line
#                     )
#
#     if len(results_all_in) > 0:
#         line = "dashed"
#
#         # configure in nodes
#         for row in results_all_in:
#             new_rela = row[1].replace("_", " ")
#
#             for label in row[0].labels:
#                 if label == 'Paper':
#                     tp = Paper.inflate(row[0])
#                     ego_json += node_temp.format(
#                         tp.id, tp.title, reverse("paper_detail", kwargs={"id": tp.id}), 'Paper', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         tp.id, '-', id, new_rela, tp.id, id, line
#                     )
#
#                 if label == 'Person':
#                     tpe = Person.inflate(row[0])
#                     middleName = ""
#                     # reformat middle name from string "['mn1', 'mn2', ...]" to array ['mn1', 'mn2', ...]
#                     if tpe.middle_name is not None:
#                         middleNames = tpe.middle_name[1:-1].split(', ')
#                         # concatenate middle names to get 'mn1 mn2 ...'
#                         for i in range(len(middleNames)):
#
#                             middleName = middleName + " " + middleNames[i][1:-1]
#
#                     middleName = middleName.replace("'", r"\'")
#                     ego_json += ", {{data : {{id: '{}', first_name: '{}', middle_name: '{}', last_name: '{}', href: '{}', " \
#                                 "type: '{}', " \
#                                 "label: '{}'}} }}".format(
#                         tpe.id, tpe.first_name, middleName, tpe.last_name,
#                         reverse("person_detail", kwargs={"id": tpe.id}), 'Person', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         tpe.id, "-", id, new_rela, tpe.id, id, line
#                     )
#
#                 if label == 'Venue':
#                     tv = Venue.inflate(row[0])
#                     ego_json += node_temp.format(
#                         tv.id, tv.name, reverse("venue_detail", kwargs={"id": tv.id}), 'Venue', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         tv.id, "-", id, new_rela, tv.id, id, line
#                     )
#                 if label == 'Dataset':
#                     td = Dataset.inflate(row[0])
#                     ego_json += node_temp.format(
#                         td.id, td.name, reverse("dataset_detail", kwargs={"id": td.id}), 'Dataset', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         td.id, "-", id, new_rela, td.id, id, line
#                     )
#
#                 if label == 'Code':
#                     tc = Code.inflate(row[0])
#                     ego_json += node_temp.format(
#                         tc.id, 'Code', reverse("code_detail", kwargs={"id": tc.id}), 'Code', new_rela
#                     )
#
#                     ego_json += rela_temp.format(
#                         tc.id, "-", id, new_rela, tc.id, id, line
#                     )
#
#     return "[" + ego_json + "]"

def paper_find(request):
    message = None
    if request.method == "POST":
        form = SearchPapersForm(request.POST)
        print("paper_find: Received POST request")
        if form.is_valid():
            paper_title = form.cleaned_data["paper_title"].lower()
            print(f"Searching for paper using keywords {paper_title}")
            papers = Paper.objects.filter(title__contains=paper_title)
            # papers = Paper.objects.annotate(
            #     search=SearchVector('title')
            # ).filter(search=SearchQuery(paper_title, search_type='plain'))
            print(papers)
            if papers:
                return render(request, "papers_index.html", {"papers": papers, "form": form, "message": message})
            else:
                message = "No results found. Please try again!"
        else:
            print("form is not valid!")

    elif request.method == "GET":
        print("paper_find: Received GET request")
        form = SearchPapersForm()

    return render(request, "papers_index.html", {"form": form, "message": message})


@login_required
def paper_connect_venue_selected(request, id, vid):

    try:
        paper = Paper.objects.get(pk=id)
        venue = Venue.objects.get(pk=vid)
        venue.paper_set.add(paper)
        messages.add_message(request, messages.INFO, "Linked with venue.")
    except ObjectDoesNotExist:
        print("Paper or venue not found in DB.")
        messages.add_message(request, messages.INFO, "Link to venue failed!")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_connect_venue(request, id):
    if request.method == "POST":
        form = SearchVenuesForm(request.POST)
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            keywords = form.cleaned_data["keywords"].lower()

            venues_found = Venue.objects.annotate(
                 search=SearchVector('name', 'keywords')
            ).filter(search=SearchQuery(keywords, search_type='plain'))

            print(venues_found)

            if venues_found.count() > 0:
                venue_connect_urls = [
                    reverse(
                        "paper_connect_venue_selected",
                        kwargs={"id": id, "vid": venue.id},
                    )
                    for venue in venues_found
                ]
                print("venue connect urls")
                print(venue_connect_urls)

                venues = zip(venues_found, venue_connect_urls)

                # ask the user to select one of them
                return render(
                    request,
                    "paper_connect_venue.html",
                    {"form": form, "venues": venues, "message": ""},
                )
            else:
                # render new Venue form with the searched name as
                message = "No matching venues found"

    if request.method == "GET":
        form = SearchVenuesForm()
        message = None

    return render(
        request,
        "paper_connect_venue.html",
        {"form": form, "venues": None, "message": message},
    )


@login_required
def paper_add_to_collection_selected(request, id, cid):
    message = None
    print("In paper_add_to_collection_selected")

    try:
        paper = Paper.objects.get(pk=id)
        collection = Collection.objects.get(pk=cid)
    except ObjectDoesNotExist:
        return Http404

    print("Found collection {}".format(collection))

    if collection.owner == request.user:
        # check if paper already exists in collection.
        paper_in_collection = collection.papers.filter(paper=paper)
        if paper_in_collection:
            message = "Paper already exists in collection {}".format(collection.name)
        else:
            c_entry = CollectionEntry()
            c_entry.collection = collection
            c_entry.paper = paper
            c_entry.save()
            message = "Paper added to collection {}".format(collection.name)
    else:
        print("collection owner does not match user")

    print(message)
    messages.add_message(request, messages.INFO, message)

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id, }))


@login_required
def paper_add_to_collection(request, id):
    print("In paper_add_to_collection")
    message = None
    # Get all collections that this person has created
    collections = Collection.objects.filter(owner=request.user)

    print("User has {} collections.".format(len(collections)))

    if len(collections) > 0:
        collection_urls = [
            reverse(
                "paper_add_to_collection_selected",
                kwargs={"id": id, "cid": collection.id},
            )
            for collection in collections
        ]

        all_collections = zip(collections, collection_urls)
    else:
        all_collections = None

    return render(
        request,
        "paper_add_to_collection.html",
        {"collections": all_collections, "message": message},
    )


@login_required
def paper_add_to_group_selected(request, id, gid):
    try:
        paper = Paper.objects.get(pk=id)
        group = ReadingGroup.objects.get(pk=gid)
    except ObjectDoesNotExist:
        return Http404

    print("Found group {}".format(group))
    paper_in_group = group.papers.filter(paper=paper)
    if paper_in_group:
        # message = "Paper already exists in group {}".format(group.name)
        print(f"Paper {paper} already exists in group {group}")
    else:
        group_entry = ReadingGroupEntry()
        group_entry.reading_group = group
        group_entry.proposed_by = request.user
        group_entry.paper = paper
        group_entry.save()
        print(f"Added paper {paper} to group {group}.")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_add_to_group(request, id):
    message = None
    # Get all reading groups that this person has created
    # Note: This should be extended to allow user to propose
    #       papers to group they belong to as well.
    groups = ReadingGroup.objects.all()

    group_urls = [
        reverse(
            "paper_add_to_group_selected",
            kwargs={"id": id, "gid": group.id},
        )
        for group in groups
    ]

    all_groups = zip(groups, group_urls)

    return render(
        request,
        "paper_add_to_group.html",
        {"groups": all_groups, "message": message},
    )


@login_required
def paper_connect_author_selected(request, id, aid):

    try:
        paper = Paper.objects.get(pk=id)
        author = Person.objects.get(pk=aid)
        author.papers.add(paper)
        messages.add_message(request, messages.INFO, "Linked with author.")
    except ObjectDoesNotExist:
        print("Paper or author not found in DB.")
        messages.add_message(request, messages.INFO, "Link to author failed!")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_connect_author(request, id):
    message = ''
    if request.method == "POST":
        form = SearchPeopleForm(request.POST)
        if form.is_valid():
            # search the db for the person
            # if the person is found, then link with paper and go back to paper view
            name = form.cleaned_data["person_name"]
            # Search for people matching the name
            people_found = Person.objects.annotate(
                 search=SearchVector('first_name', 'last_name', 'middle_name')
            ).filter(search=SearchQuery(name, search_type='plain'))

            print(people_found)

            if people_found is not None:
                print("Found {} people that match".format(len(people_found)))
                for person in people_found:
                    print(
                        "\t{} {} {}".format(
                            person.first_name, person.middle_name, person.last_name
                        )
                    )

                if people_found.count() > 0:
                    author_connect_urls = [
                        reverse(
                            "paper_connect_author_selected",
                            kwargs={"id": id, "aid": person.id},
                        )
                        for person in people_found
                    ]
                    print("author connect urls")
                    print(author_connect_urls)

                    authors = zip(people_found, author_connect_urls)

                    # ask the user to select one of them
                    return render(
                        request,
                        "paper_connect_author.html",
                        {"form": form, "people": authors, "message": ""},
                    )
            else:
                message = "No matching people found"

    if request.method == "GET":
        form = SearchPeopleForm()
        message = None

    return render(
        request,
        "paper_connect_author.html",
        {"form": form, "people": None, "message": message},
    )


@login_required
def paper_connect_paper_selected(request, id, pid):

    paper_from = get_object_or_404(Paper, pk=id)
    paper_to = get_object_or_404(Paper, pk=pid)

    print(f"paper_from: {paper_from}")
    print(f"paper_to: {paper_to}")

    # Check if a relationship between the two papers exists.
    # If it does, delete it before adding a new relationship.
    edges = PaperRelationshipType(paper_from=paper_from, paper_to=paper_to)
    if edges:
        # Found existing relationship so remove it.
        print(f"Found {edges} existing relationships and will delete them.")
        paper_from.papers.remove(paper_to)

    # We have the two Paper objects.
    # Add the relationship between them.
    print("Adding the new relationship.")
    # add the new link
    # TODO: Check if the link exists, does it add it again?
    # TODO: Two papers should only be linked by one type of relationship so check if one exists, delete, and create
    # a new one.
    link_type = request.session["link_type"]
    print(f"link_type: {link_type}")
    edge = PaperRelationshipType(paper_from=paper_from,
                                 paper_to=paper_to,
                                 relationship_type=link_type)
    edge.save()
    print(edge)
    messages.add_message(request, messages.INFO, "Connection Added!")

    return redirect("paper_detail", id=id)


@login_required
def paper_connect_paper(request, id):
    """
    View function for connecting a paper with another paper.
    :param request:
    :param id:
    :return:
    """
    message = None
    if request.method == "POST":
        form = PaperConnectionForm(request.POST)
        if form.is_valid():
            # search the db for the person
            # if the person is found, then link with paper and go back to paper view
            # if not, ask the user to create a new person
            paper_title_query = form.cleaned_data["paper_title"]
            print(f"Searching for paper using keywords {paper_title_query}")
            papers_found = Paper.objects.annotate(
                 search=SearchVector('title')
            ).filter(search=SearchQuery(paper_title_query, search_type='plain'))
            print(papers_found)

            paper_relationship = form.cleaned_data["paper_connection"]

            if papers_found.count() > 0:  # found more than one matching papers
                print("Found {} papers that match".format(len(papers_found)))
                for paper in papers_found:
                    print("\t{}".format(paper.title))

                    paper_connect_urls = [
                        reverse(
                            "paper_connect_paper_selected",
                            kwargs={"id": id, "pid": paper.id},
                        )
                        for paper in papers_found
                    ]
                    print("paper connect urls")
                    print(paper_connect_urls)

                    papers = zip(papers_found, paper_connect_urls)
                    #
                    # TODO: pass the relationship type in a better way than through a session variable.
                    #
                    request.session["link_type"] = paper_relationship
                    # ask the user to select one of them
                    return render(
                        request,
                        "paper_connect_paper.html",
                        {"form": form, "papers": papers, "message": ""},
                    )
            else:
                message = "No matching papers found"

    if request.method == "GET":
        form = PaperConnectionForm()

    return render(
        request,
        "paper_connect_paper.html",
        {"form": form, "papers": None, "message": message},
    )


@login_required
def paper_connect_dataset_selected(request, id, did):

    try:
        paper = Paper.objects.get(pk=id)
        dataset = Dataset.objects.get(pk=did)
        dataset.papers.add(paper)
        messages.add_message(request, messages.INFO, "Linked with dataset.")
    except ObjectDoesNotExist:
        print("Dataset or paper not found in DB.")
        messages.add_message(request, messages.INFO, "Link to dataset failed!")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_connect_dataset(request, id):
    """
    View function for connecting a paper with a dataset.

    :param request:
    :param id:
    :return:
    """
    message = "No matching datasets found."
    if request.method == "POST":
        form = SearchDatasetsForm(request.POST)
        if form.is_valid():
            # search the db for the dataset
            # if the dataset is found, then link with paper and go back to paper view
            dataset_query_keywords = form.cleaned_data["keywords"]

            print(f"Searching for dataset using keywords {dataset_query_keywords}")

            datasets_found = Dataset.objects.annotate(
                search=SearchVector('keywords', 'name')
            ).filter(search=SearchQuery(dataset_query_keywords, search_type='plain'))

            print(datasets_found)

            if datasets_found is not None:  # found more than one matching dataset
                print("Found {} datasets that match".format(datasets_found.count()))
                for dataset in datasets_found:
                    print("\t{}".format(dataset.name))

                if datasets_found.count() > 0:
                    # for rid in relationship_ids:
                    datasets_connect_urls = [
                        reverse(
                            "paper_connect_dataset_selected",
                            kwargs={"id": id, "did": dataset.id},
                        )
                        for dataset in datasets_found
                    ]
                    print(datasets_connect_urls)

                    datasets = zip(datasets_found, datasets_connect_urls)

                    # ask the user to select one of them
                    return render(
                        request,
                        "paper_connect_dataset.html",
                        {"form": form, "datasets": datasets, "message": ""},
                    )
            else:
                message = "No matching datasets found"

    if request.method == "GET":
        form = SearchDatasetsForm()
        message = None

    return render(
        request,
        "paper_connect_dataset.html",
        {"form": form, "datasets": None, "message": message},
    )


@login_required
def paper_connect_code_selected(request, id, cid):

    paper = get_object_or_404(Paper, pk=id)
    code = get_object_or_404(Code, pk=cid)
    code.papers.add(paper)
    messages.add_message(request, messages.INFO, "Linked with code repo.")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_connect_code(request, id):
    """
    View function for connecting a paper with a dataset.

    :param request:
    :param id:
    :return:
    """
    message = ""
    if request.method == "POST":
        form = SearchCodesForm(request.POST)
        if form.is_valid():
            # search the db for the person
            # if the person is found, then link with paper and go back to paper view
            # if not, ask the user to create a new person
            keywords = form.cleaned_data["keywords"]
            codes_found = Code.objects.annotate(
                 search=SearchVector('keywords',)
            ).filter(search=SearchQuery(keywords, search_type='plain'))

            print(codes_found)

            if codes_found is not None:
                print("Found {} codes that match".format(codes_found.count()))
                for code in codes_found:
                    print("\t{} {}".format(code.website, code.keywords))

                if codes_found.count() > 0:
                    # for rid in relationship_ids:
                    codes_connect_urls = [
                        reverse(
                            "paper_connect_code_selected",
                            kwargs={"id": id, "cid": code.id},
                        )
                        for code in codes_found
                    ]
                    print(codes_connect_urls)

                    codes = zip(codes_found, codes_connect_urls)

                    # ask the user to select one of them
                    return render(
                        request,
                        "paper_connect_code.html",
                        {"form": form, "codes": codes, "message": ""},
                    )
            else:
                message = "No matching codes found"

    if request.method == "GET":
        form = SearchCodesForm()
        message = None

    return render(
        request,
        "paper_connect_code.html",
        {"form": form, "codes": None, "message": message},
    )


@login_required
def paper_update(request, id):
    try:
        paper_inst = Paper.objects.filter(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("papers_index"))

    paper = paper_inst.first()

    # if this is POST request then process the Form data
    if request.method == "POST":

        form = PaperForm(request.POST)
        if form.is_valid():
            paper.title = form.cleaned_data["title"]
            paper.abstract = form.cleaned_data["abstract"]
            paper.keywords = form.cleaned_data["keywords"]
            paper.download_link = form.cleaned_data["download_link"]
            paper.save()

            return HttpResponseRedirect(reverse("papers_index"))
    # GET request
    else:
        form = PaperForm(
            initial={
                "title": paper.title,
                "abstract": paper.abstract,
                "keywords": paper.keywords,
                "download_link": paper.download_link,
            }
        )

    return render(request, "paper_update.html", {"form": form, "paper": paper})


def _add_author(author, paper=None):
    """
    Adds author to the DB if author does not already exist and links to paper
    as author if paper is not None
    :param author <str>: Author name
    :param paper:
    """
    link_with_paper = False
    author_name = author.strip().split(" ")

    if len(author_name) > 2:
        people_found = Person.objects.filter(first_name=author_name[0],
                                             middle_name=author_name[1],
                                             last_name=author_name[2])
    else:
        people_found = Person.objects.filter(first_name=author_name[0], last_name=author_name[1])

    print("**** People matching query {} ****".format(author_name))
    print(people_found)

    if people_found.count() == 0:  # not in DB
        print("Author {} not in DB".format(author))
        p = Person()
        p.first_name = author_name[0]

        if len(author_name) > 2:  # has middle name(s)
            p.middle_name = author_name[1:-1]
        # else:
        #     p.middle_name = None
        p.last_name = author_name[-1]
        print("**** Person {} ***".format(p))
        p.save()  # save to DB
        link_with_paper = True
    elif people_found.count() == 1:
        # Exactly one person found. Check if name is an exact match.
        p = people_found[0]
        print("Author {} found in DB with name {}".format(author_name, p))
        # NOTE: The problem with this simple check is that if two people have
        # the same name then the wrong person will be linked to the paper.
        if p.first_name == author_name[0] and p.last_name == author_name[-1]:
            if len(author_name) > 2:
                if p.middle_name == author_name[1:-1]:
                    link_with_paper = True
            else:
                link_with_paper = True
    else:
        print("Person with similar but not exactly the same name is already in DB.")

    if link_with_paper and paper is not None:
        print("Adding authors link to paper {}".format(paper.title[:50]))
        # link author with paper
        p.papers.add(paper)


@login_required
def paper_create(request):
    user = request.user
    print("In paper_create() view.")
    message = ""
    if request.method == "POST":
        print("   POST")
        paper = Paper()
        paper.created_by = user
        form = PaperForm(instance=paper, data=request.POST)
        if form.is_valid():
            # Check if the paper already exists in DB
            # Exact match on title.
            matching_papers = Paper.objects.filter(title=form.cleaned_data["title"])
            if matching_papers.count() > 0:  # paper in DB already
                message = "Paper already exists in Gnosis!"
                return render(
                    request,
                    "paper_results.html",
                    {"papers": matching_papers, "message": message},
                )
            else:  # the paper is not in DB yet.
                form.save()  # store
                # Now, add the authors and link each author to the paper with an "authors"
                # type edge.
                if request.session.get("from_external", False):
                    paper_authors = request.session["external_authors"]
                    for paper_author in reversed(paper_authors.split(",")):
                        print("Adding author {}".format(paper_author))
                        _add_author(paper_author, paper)

                request.session["from_external"] = False  # reset
                # go back to paper index page.
                # Should this redirect to the page of the new paper just added?
                return HttpResponseRedirect(reverse("papers_index"))
    else:  # GET
        print("   GET")
        # check if this is a redirect from paper_create_from_url
        # if so, then pre-populate the form with the data from external source,
        # otherwise start with an empty form.
        if request.session.get("from_external", False) is True:
            title = request.session["external_title"]
            abstract = request.session["external_abstract"]
            url = request.session["external_url"]
            download_link = request.session["download_link"]

            form = PaperForm(
                initial={"title": title, "abstract": abstract, "download_link": download_link, "source_link": url}
            )
        else:
            form = PaperForm()

    return render(request, "paper_form.html", {"form": form, "message": message})


def get_authors(bs4obj, source_website):
    """
    Extract authors from the source website
    :param bs4obj, source_website；
    :return: None or a string with comma separated author names from first to last name
    """
    if source_website == "arxiv":
        return get_authors_from_arxiv(bs4obj)
    elif source_website == 'nips':
        return get_authors_from_nips(bs4obj)
    elif source_website == "jmlr":
        return get_authors_from_jmlr(bs4obj)
    elif source_website == "ieee":
        return get_authors_from_IEEE(bs4obj)
    elif source_website == "acm":
        return get_authors_from_ACM(bs4obj)
    # if source website is not supported or the autherlist is none , return none
    return None


def get_title(bs4obj, source_website):
    """
    Extract paper title from the source web.
    :param bs4obj:
    :return:
    """
    if source_website == "arxiv":
        titleList = bs4obj.findAll("h1", {"class": "title"})
    elif source_website == 'nips':
        titleList = bs4obj.findAll("title")
    elif source_website == "jmlr":
        titleList = bs4obj.findAll("h2")
    elif source_website == "ieee":
        title = bs4obj.find("title").get_text()
        i = title.find("- IEEE")
        if i != -1:
            title = title[0:i]
        return title
    elif source_website == "acm":
        titleList = bs4obj.find("meta", {"name": "citation_title"})
        title = str(titleList)
        start = title.find('"')
        end = title.find('"', start + 1)
        title = title[start + 1:end]
        if title == "Non":
            return None
        return title
    else:
        titleList = []
    # check the validity of the abstracted titlelist
    if titleList:
        if len(titleList) == 0:
            return None
        else:
            if len(titleList) > 1:
                print("WARNING: Found more than one title. Returning the first one.")
            # return " ".join(titleList[0].get_text().split()[1:])
            title_text = titleList[0].get_text()
            if title_text.startswith("Title:"):
                return title_text[6:]
            else:
                return title_text
    return None

def get_abstract(bs4obj, source_website):
    """
    Extract paper abstract from the source website.
    :param bs4obj, source_website:
    :return:
    """
    if source_website == "arxiv":
        abstract = bs4obj.find("blockquote", {"class": "abstract"})
        if abstract is not None:
            abstract = " ".join(abstract.get_text().split(" ")[1:])
    elif source_website == 'nips':
        abstract = bs4obj.find("p", {"class": "abstract"})
        if abstract is not None:
            abstract = abstract.get_text()
    elif source_website == "jmlr":
        abstract = bs4obj.find("p", {"class": "abstract"})
        if abstract is not None:
            abstract = abstract.get_text()
        else:
            # for some papers from JMLR , the abstract is stored without a tag,so this will find the abstract
            abstract = bs4obj.find("h3")
            if abstract is not None:
                abstract = abstract.next_sibling
    elif source_website == "ieee":
        abstract = get_abstract_from_IEEE(bs4obj)
    elif source_website == "acm":
        abstract = get_abstract_from_ACM(bs4obj)
    else:
        abstract = None
    # want to remove all the leading and ending white space and line breakers in the abstract
    if abstract is not None:
        abstract = abstract.strip()
        if source_website != "arxiv":
            abstract = abstract.replace('\r', '').replace('\n', '')
        else:
            abstract = abstract.replace('\n', ' ')
    return abstract


def get_venue(bs4obj):
    """
    Extract publication venue from arXiv.org paper page.
    :param bs4obj:
    :return:
    """
    venue = bs4obj.find("td", {"class": "tablecell comments mathjax"})
    if venue is not None:
        venue = venue.get_text().split(";")[0]
    return venue


# this function is used to find the download_link for a paper from IEEE

def get_download_link(bs4obj, source_website, url):
    """
    Extract download link from paper page1
    :param bs4obj:
    return: download link of paper
    """
    if url.endswith("/"):
        url = url[:-1]
    if source_website == "arxiv":
        download_link = url.replace("/abs/", "/pdf/", 1) + ".pdf"
    elif source_website == "nips":
        download_link = url + ".pdf"
    elif source_website == "jmlr":
        download_link = bs4obj.find(href=re.compile("pdf"))['href']
        print(download_link)
        if download_link.startswith("/papers/"):
            download_link = "http://www.jmlr.org" + download_link
    elif source_website == "ieee":
        download_link = get_ddl_from_IEEE(bs4obj)
    elif source_website == "acm":
        download_link = bs4obj.find("meta", {"name": "citation_pdf_url"})
        download_link = str(download_link)
        start = download_link.find('"')
        end = download_link.find('"', start + 1)
        download_link = download_link[start + 1:end]
        return download_link
    else:
        download_link = None
    return download_link


def get_paper_info(url, source_website):
    """
    Extract paper information, title, abstract, and authors, from source website
    paper page.
    :param url, source_website:
    :return:
    """
    try:
        # html = urlopen("http://pythonscraping.com/pages/page1.html")
        url_copy = url
        if source_website == "acm":
            headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
            url = Request(url, headers=headers)
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
        print("The server could not be found.")
    else:
        bs4obj = BeautifulSoup(html, features="html.parser")
        if source_website == "ieee":
            if check_valid_paper_type_ieee(bs4obj) == False:
                return None, None, None, None
        if source_website == "acm":
            url = ""
            if bs4obj.find("a", {"title": "Buy this Book"}) or bs4obj.find("a", {"ACM Magazines"}) \
                    or bs4obj.find_all("meta", {"name": "citation_conference_title"}):
                return None, None, None, None
        # Now, we can access individual element in the page
        authors = get_authors(bs4obj, source_website)
        title = get_title(bs4obj, source_website)
        abstract = get_abstract(bs4obj, source_website)
        download_link = ""
        if authors and title and abstract:
            download_link = get_download_link(bs4obj, source_website, url)
        if download_link == "Non":
            download_link = url_copy
        # venue = get_venue(bs4obj)
        return title, authors, abstract, download_link

    return None, None, None, None


@login_required
def paper_create_from_url(request):
    user = request.user

    if request.method == "POST":
        # create the paper from the extracted data and send to
        # paper_form.html asking the user to verify
        print("{}".format(request.POST["url"]))
        # get the data from arxiv
        url = request.POST["url"]

        validity,source_website,url = analysis_url(url)
        # return error message if the website is not supported
        if validity == False:
            form = PaperImportForm()
            return render(
                request,
                "paper_form.html",
                {"form": form, "message": "Source website is not supported"},
            )
        # retrieve paper info. If the information cannot be retrieved from remote
        # server, then we will return an error message and redirect to paper_form.html.
        title, authors, abstract, download_link = get_paper_info(url, source_website)
        if title is None or authors is None or abstract is None:
            form = PaperImportForm()
            return render(
                request,
                "paper_form.html",
                {"form": form, "message": "Invalid source, please try again."},
            )

        request.session["from_external"] = True
        request.session["external_title"] = title
        request.session["external_abstract"] = abstract
        request.session["external_url"] = url
        request.session["download_link"] = download_link
        request.session[
            "external_authors"
        ] = authors  # comma separate list of author names, first to last name

        print("Authors: {}".format(authors))

        return HttpResponseRedirect(reverse("paper_create"))
    else:  # GET
        request.session["from_external"] = False
        form = PaperImportForm()

    return render(request, "paper_form.html", {"form": form})

#
# Venue Views
#
def venues(request):
    all_venues = Venue.objects.all()
    # all_venues = Venue.nodes.order_by("-publication_date")[:50]

    message = None
    if request.method == "POST":
        form = SearchVenuesForm(request.POST)
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            venue_name = form.cleaned_data["keywords"].lower()
            # venue_publication_year = form.cleaned_data["venue_publication_year"]

            print(f"Searching for venue using keywords {venue_name}")

            venues_found = Venue.objects.annotate(
                 search=SearchVector('name', 'keywords')
            ).filter(search=SearchQuery(venue_name, search_type='plain'))

            if venues_found.count() > 0:
                print("Found {} venues that match".format(venues_found.count()))
                return render(request, "venues.html", {"venues": venues_found, "form": form, "message": message})
            else:
                # render new Venue form with the searched name as
                message = "No matching venues found"

    if request.method == "GET":
        form = SearchVenuesForm()
        message = None

    return render(request, "venues.html", {"venues": all_venues, "form": form, "message": message})


def venue_detail(request, id):
    papers_published_at_venue = None
    # Retrieve the paper from the database
    try:
        venue = Venue.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("venues_index"))

    print(f"Papers published at this venue {venue.paper_set.all()}")

    request.session["last-viewed-venue"] = id
    return render(request, "venue_detail.html", {"venue": venue, "papers": venue.paper_set.all()})


def venue_find(request):
    """
    Search for venue.
    :param request:
    :return:
    """
    message = None
    if request.method == "POST":
        form = SearchVenuesForm(request.POST)
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            venue_name = form.cleaned_data["venue_name"].lower()
            venue_publication_year = form.cleaned_data["venue_publication_year"]

            print(f"Searching for venue using keywords {venue_name} and year {venue_publication_year}")

            venues_found = Venue.objects.annotate(
                 search=SearchVector('name', 'keywords')
            ).filter(search=SearchQuery(venue_name, search_type='plain'))

            if venues_found.count() > 0:
                print("Found {} venues that match".format(venues_found.count()))
                return render(request, "venues.html", {"venues": venues})
            else:
                # render new Venue form with the searched name as
                message = "No matching venues found"

    if request.method == "GET":
        form = SearchVenuesForm()
        message = None

    return render(request, "venue_find.html", {"form": form, "message": message})


@login_required
def venue_create(request):

    if request.method == "POST":
        venue = Venue()
        venue.created_by = request.user
        form = VenueForm(instance=venue, data=request.POST)
        if form.is_valid():
            # check if venue already in database and do not add it if so.
            venue_name = form.clean_name()
            venue_year = form.clean_publication_year()
            venue_year = int(venue_year)
            other_venues = Venue.objects.filter(name__iexact=venue_name, publication_year=venue_year)
            if other_venues.count() == 0:
                print("Found no other matching venues")
                form.save()
            else:
                print(f"Found {other_venues.count()} matching venues.")
            return HttpResponseRedirect(reverse("venues_index"))
    else:  # GET
        form = VenueForm()

    return render(request, "venue_form.html", {"form": form})


# should limit access to admin users only!!
@staff_member_required
def venue_delete(request, id):

    print("WARNING: Deleting venue id {} and all related edges".format(id))
    try:
        venue = Venue.objects.get(pk=id)
        venue.delete()
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("venues_index"))

    return HttpResponseRedirect(reverse("venues_index"))


@login_required
def venue_update(request, id):

    try:
        venue = Venue.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("venues_index"))

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            venue.name = form.cleaned_data["name"]
            venue.publication_year = form.cleaned_data["publication_year"]
            venue.publication_month = form.cleaned_data["publication_month"]
            venue.venue_type = form.cleaned_data["venue_type"]
            venue.publisher = form.cleaned_data["publisher"]
            venue.keywords = form.cleaned_data["keywords"]
            venue.peer_reviewed = form.cleaned_data["peer_reviewed"]
            venue.website = form.cleaned_data["website"]
            venue.save()
            return HttpResponseRedirect(reverse("venue_detail", kwargs={"id": id}))
    # GET request
    else:
        form = VenueForm(
            initial={
                "name": venue.name,
                "venue_type": venue.venue_type,
                "publication_year": venue.publication_year,
                "publication_month": venue.publication_month,
                "publisher": venue.publisher,
                "keywords": venue.keywords,
                "peer_reviewed": venue.peer_reviewed,
                "website": venue.website,
            }
        )

    return render(request, "venue_update.html", {"form": form, "venue": venue})

#
# Utility Views (admin required)
#
@login_required
def build(request):
    num_papers = Paper.objects.all().count()
    num_people = Person.objects.all().count()

    return render(
        request, "build.html", {"num_papers": num_papers, "num_people": num_people}
    )
