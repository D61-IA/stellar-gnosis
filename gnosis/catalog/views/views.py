from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from catalog.models import (
    Paper,
    PaperRelationshipType,
    Person,
    PaperAuthorRelationshipData,
    Dataset,
    Venue,
    Comment,
    CommentFlag,
    Code,
)
from django.http import Http404, HttpResponseBadRequest
from catalog.models import Paper, Person, Dataset, Venue, Comment, Code, CommentFlag
from notes.forms import NoteForm
from notes.models import Note
from catalog.models import ReadingGroup, ReadingGroupEntry
from catalog.models import Collection, CollectionEntry
from catalog.models import Endorsement
from bookmark.models import Bookmark
from catalog.views.utils.import_functions import *
from catalog.views.utils.classes import UserComment

from catalog.forms import (
    PaperForm,
    PaperUpdateForm,
    DatasetForm,
    VenueForm,
    CommentForm,
    PaperImportForm,
    FlaggedCommentForm,
)

from catalog.forms import (
    SearchAllForm,
    SearchVenuesForm,
    SearchPapersForm,
    SearchPeopleForm,
    SearchDatasetsForm,
    SearchCodesForm,
    PaperConnectionForm,
)

from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from django.contrib import messages
from itertools import chain


#
# Paper Views
def papers(request):
    # Retrieve the papers ordered by newest addition to DB first.
    # limit to maximum 50 papers until we get pagination to work.
    # However, even with pagination, we are going to want to limit
    # the number of papers retrieved for speed, especially when the
    # the DB grows large.
    all_papers = Paper.objects.filter(is_public=True).order_by("-created_at")[:100]
    results_message = ''
    if request.method == "POST":
        form = SearchPapersForm(request.POST) 
        print("papers: Received POST request")
        if form.is_valid():
            paper_title = form.cleaned_data["paper_title"].lower()
            print(f"Searching for paper using keywords {paper_title}")

            papers = Paper.objects.annotate(search=SearchVector("title")).filter(
                search=SearchQuery(paper_title, search_type="plain"), is_public=True,
            )
            print(papers)
            num_papers_found = len(papers)            
            if papers:
                if num_papers_found > 25:
                    papers = papers[:25]
                    results_message = f"Showing 25 out of {num_papers_found} paper found. For best results, please narrow your search."
            else:
                results_message = "No results found. Please try again!"
            
            return render(
                    request,
                    "paper_results.html",
                    {"papers": papers, "form": form, "results_message": results_message},
                )


    elif request.method == "GET":
        print("papers: Received GET request")
        form = SearchPapersForm()

    return render(
        request, "papers.html", {"papers": all_papers, "form": form}
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

    return render(
        request,
        "paper_authors.html",
        {"authors": authors, "paper": paper, "number_of_authors": num_authors},
    )


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
    # What does this return? How can I make certain that the author was deleted?

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
        rel_model = PaperRelationshipType.objects.get(
            paper_from=paper, paper_to=paper_to
        )
        print(f"{rel_model.relationship_type}")

    endorsed, bookmarked = False, False

    # Retrieve all notes that created by the current user and on current paper.
    notes = []
    if request.user.is_authenticated:
        notes = Note.objects.filter(paper=paper, created_by=request.user)
        # Get if paper is endorsed or bookmarked by the user
        endorsed = paper.endorsements.filter(user=request.user).exists()
        bookmarked = paper.bookmarks.filter(owner=request.user).exists()

    # Retrieve the paper's authors
    # authors is a list of strings so just concatenate the strings.
    authors_set = PaperAuthorRelationshipData.objects.filter(paper=paper).order_by('order')
    print(f"** Retrieved authors {authors_set}")

    authors = []
    for author in authors_set:
        authors.append(author.author.name)
    authors = ", ".join(authors)

    codes = paper.code_set.all()
    datasets = paper.dataset_set.all()
    print(datasets)
    venue = paper.was_published_at

    ego_network_json = _get_node_ego_network(paper.id)

    # Comment / Note form
    note_form = NoteForm()
    comment_form = CommentForm()
    if request.method == "POST":
        # success = False
        if "comment_form" in request.POST:
            comment = Comment(created_by=request.user, paper=paper)
            comment_form = CommentForm(instance=comment, data=request.POST)
            if comment_form.is_valid():
                comment_form.save()
                # Create a new empty form for display
                comment_form = CommentForm()
        elif "note_form" in request.POST:
            note = Note(created_by=request.user, paper_id=paper.id)
            note_form = NoteForm(instance=note, data=request.POST)
            if note_form.is_valid():
                note_form.save()
                note_form = NoteForm()

    comments = paper.comment_set.all()
    flag_form = FlaggedCommentForm()

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
            "noteform": note_form,
            "notes": notes,
            "commentform": comment_form,
            "flag_form": flag_form,
            "num_comments": comments.count(),
            "endorsed": endorsed,
            "bookmarked": bookmarked,
            "ego_network": ego_network_json,
        },
    )


def _get_paper_paper_network(main_paper, ego_json):
    # type refers to what node type the object is associated with.
    # label refers to the text on the object.
    node_temp = (
        ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"
    )
    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    # papers_out = main_paper.papers.all()  #
    papers_out = PaperRelationshipType.objects.filter(paper_from=main_paper)
    papers_in = PaperRelationshipType.objects.filter(paper_to=main_paper)

    # Sort nodes and store them in arrays accordingly
    # 'out' refers to being from the paper to the object
    # line property for out
    line = "solid"
    for paper_out in papers_out:
        paper = paper_out.paper_to
        ego_json += node_temp.format(
            paper.id,
            paper.title,
            reverse("paper_detail", kwargs={"id": paper.id}),
            "Paper",
            paper_out.relationship_type,
        )
        # adding relationship with paper node
        ego_json += rela_temp.format(
            main_paper.id,
            "-",
            paper.id,
            "Paper",
            paper_out.relationship_type,
            main_paper.id,
            paper.id,
            line,
        )

    line = 'dashed'
    for paper_in in papers_in:
        paper = paper_in.paper_from
        ego_json += node_temp.format(
            paper.id,
            paper.title,
            reverse("paper_detail", kwargs={"id": paper.id}),
            "Paper",
            paper_in.relationship_type,
        )
        # adding relationship with paper node
        ego_json += rela_temp.format(
            main_paper.id,
            "-",
            paper.id,
            "Paper",
            paper_in.relationship_type,
            paper.id,
            main_paper.id,
            line,
        )

    return ego_json


def _get_paper_author_network(main_paper, ego_json, offset=101):
    """

    :param main_paper:
    :param ego_json:
    :param offset: This is a massive hack to avoid papers and authors having the same ID. It can still happen with the
    offset but for now it helps. I really need to have a look at this again.
    
    :return:
    """
    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"
    author_str = ", {{data : {{id: '{}', name: '{}', href: '{}', type: '{}', label: '{}'}} }}"
    # query for everything that points to the paper
    paper_authors = main_paper.person_set.all()

    line = "dashed"
    for author in paper_authors:
        ego_json += author_str.format(
            author.id + offset,
            author.name,
            reverse("person_detail", kwargs={"id": author.id}),
            "Person",
            "authors",
        )
        ego_json += rela_temp.format(
            main_paper.id,
            "-",
            author.id + offset,
            "Person",
            "authors",
            author.id + offset,
            main_paper.id,
            line,
        )

    return ego_json


def _get_paper_venue_network(main_paper, ego_json, offset=50):

    node_temp = ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"

    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    venue = main_paper.was_published_at

    if venue:
        ego_json += node_temp.format(venue.id + offset,
                                     venue.name,
                                     reverse("venue_detail", kwargs={"id": venue.id}),
                                     'Venue', 'was published at')

        ego_json += rela_temp.format(main_paper.id,
                                     '-',
                                     venue.id + offset,
                                     'Venue',
                                     'was published at',
                                     main_paper.id,
                                     venue.id + offset,
                                     'solid')

    return ego_json


def _get_paper_dataset_network(main_paper, ego_json, offset=150):

    node_temp = ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"

    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    datasets = main_paper.dataset_set.all()

    for dataset in datasets:
        ego_json += node_temp.format(dataset.id + offset,
                                     dataset.name,
                                     reverse("dataset_detail", kwargs={"id": dataset.id}),
                                     'Dataset',
                                     'evaluates on')

        ego_json += rela_temp.format(main_paper.id,
                                     '-',
                                     dataset.id + offset,
                                     'Dataset',
                                     'evaluates on',
                                     main_paper.id,
                                     dataset.id + offset, 'solid')

    return ego_json


def _get_paper_code_network(main_paper, ego_json, offset=200):

    node_temp = ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"

    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    codes = main_paper.code_set.all()

    for code in codes:
        ego_json += node_temp.format(code.id + offset,
                                     'Code',
                                     reverse("code_detail", kwargs={"id": code.id}),
                                     'Code',
                                     'implements')
        ego_json += rela_temp.format(main_paper.id,
                                     '-',
                                     code.id + offset,
                                     'Code',
                                     'implements',
                                     code.id + offset,
                                     main_paper.id,
                                     'dashed')

    return ego_json


def _get_node_ego_network(id):
    """
     Returns a json formatted string of the nodes ego network
     :param id: The paper id/primary key
     :return:
    """
    paper = get_object_or_404(Paper, pk=id)

    # The paper is the central node in the graph
    ego_json = "{{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}'}} }}".format(
        id, paper.title, reverse("paper_detail", kwargs={"id": id}), "Paper", "origin"
    )

    # The paper-paper relationships.
    # For now, only the outgoing edges are shown.
    # ToDo: Update to include the incoming edges as well.
    ego_json = _get_paper_paper_network(main_paper=paper, ego_json=ego_json)

    ego_json = _get_paper_author_network(paper, ego_json)
    ego_json = _get_paper_venue_network(paper, ego_json)
    ego_json = _get_paper_dataset_network(paper, ego_json)
    ego_json = _get_paper_code_network(paper, ego_json)

    return "[" + ego_json + "]"


def paper_find(request):
    keywords = request.GET.get("keywords", "")
    papers = Paper.objects.filter(title__icontains=keywords)

    return render(request, "papers.html", {"papers": papers})


@login_required
def paper_connect_venue_selected(request, id, vid):
    try:
        paper = Paper.objects.get(pk=id)
        venue = Venue.objects.get(pk=vid)
        venue.paper_set.add(paper)
        messages.add_message(request, messages.INFO, "Linked with venue.")
    except ObjectDoesNotExist:
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
                search=SearchVector("name", "keywords")
            ).filter(search=SearchQuery(keywords, search_type="plain"))

            print(venues_found)

            if venues_found.count() > 0:
                venue_connect_urls = [
                    reverse(
                        "paper_connect_venue_selected",
                        kwargs={"id": id, "vid": venue.id},
                    )
                    for venue in venues_found
                ]

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

    try:
        paper = Paper.objects.get(pk=id)
        collection = Collection.objects.get(pk=cid)
    except ObjectDoesNotExist:
        return Http404

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

    messages.add_message(request, messages.INFO, message)

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


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
def paper_bookmark(request, id):
    """input:
    pid: paper id
    """
    if request.method == "POST":
        paper = get_object_or_404(Paper, pk=id)
        # Check if the bookmarks already exist
        bookmark = Bookmark.objects.filter(owner=request.user, paper=paper)
        response = {'bookmark': ""}
        if not bookmark:
            print(f"Bookmarking paper {paper}")
            bookmark = Bookmark(owner=request.user, paper=paper)
            bookmark.save()
            response['result'] = "add"
        else:
            print("Bookmark already exists so deleting it.")
            bookmark.delete()
            response['result'] = "delete"

        return JsonResponse(response)
    else:
        print("GET request")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_add_note(request, id):
    """
    Adds a note to a paper.
    """
    paper = get_object_or_404(Paper, pk=id)

    if request.method == "POST":
        note = Note()
        note.created_by = request.user
        note.paper = paper
        form = NoteForm(instance=note, data=request.POST)
        if form.is_valid():
            # add link from new comment to paper
            form.save()
            return redirect("paper_detail", id=paper.id)
    else:  # GET
        form = CommentForm()

    return render(request, "note_form.html", {"form": form})


@login_required
def paper_add_to_group_selected(request, id, gid):
    paper = get_object_or_404(Paper, pk=id)
    group = get_object_or_404(ReadingGroup, pk=gid)
    # Check if the user has permission to propose a paper for this group.
    # If group is public then all good.
    # If the group is private then check if user is a member of this group.
    q_set = group.members.filter(member=request.user).all()
    # user can only propose a paper for a group if she is the group owner or has joined a public group
    # or has been granted access to a private group.
    if group.owner == request.user or (q_set.count() == 1 and q_set[0].access_type == 'granted'):
        paper_in_group = group.papers.filter(paper=paper)
        if paper_in_group:
            # message = "Paper already exists in group {}".format(group.name)
            messages.add_message(request, messages.INFO, f"Paper {paper} has already been proposed for group {group}.")
        else:
            group_entry = ReadingGroupEntry()
            group_entry.reading_group = group
            group_entry.proposed_by = request.user
            group_entry.paper = paper
            group_entry.save()
            messages.add_message(request, messages.INFO, f"Paper successfully proposed for group {group}. Thank you!")
    else:
        messages.add_message(request, messages.INFO, "You must join the group before you can propose papers.")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_add_to_group(request, id):
    message = None
    # The public reading groups that the user has joined
    groups = ReadingGroup.objects.filter(is_public=True, members__member=request.user, members__access_type='granted')
    # The private reading groups the user has been granted access to.
    # This excludes the user who owns/created the group!
    groups_private = ReadingGroup.objects.filter(is_public=False, members__member=request.user,
                                                 members__access_type='granted')
    groups_owner = ReadingGroup.objects.filter(owner=request.user)
    # Combine the Query sets
    groups = list(chain(groups, groups_owner, groups_private))

    if len(groups) > 0:
        group_urls = [
            reverse("paper_add_to_group_selected", kwargs={"id": id, "gid": group.id})
            for group in groups
        ]

        all_groups = zip(groups, group_urls)
    else:
        all_groups = None

    return render(
        request, "paper_add_to_group.html", {"groups": all_groups, "message": message}
    )


@login_required
@staff_member_required
def paper_connect_author_selected(request, id, aid):
    '''
    ToDo: This method needs to be improved in order to allow the user to specify the author order.
    :param request:
    :param id:
    :param aid:
    :return:
    '''
    paper = get_object_or_404(Paper, pk=id)
    author = get_object_or_404(Person, pk=aid)

    author.papers.add(paper)
    messages.add_message(request, messages.INFO, "Linked with author.")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
@staff_member_required
def paper_connect_author(request, id):
    message = ""
    if request.method == "POST":
        form = SearchPeopleForm(request.POST)
        if form.is_valid():
            # search the db for the person
            # if the person is found, then link with paper and go back to paper view
            name = form.cleaned_data["person_name"]
            # Search for people matching the name
            people_found = Person.objects.annotate(
                search=SearchVector("name")
            ).filter(search=SearchQuery(name, search_type="plain"))

            if people_found is not None:

                for person in people_found:
                    print(
                        "\t{}".format(
                            person.name
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

    if paper_from == paper_to:
        messages.add_message(request, messages.INFO, "You cannot connect a paper with itself.")
    else:
        # Check if a relationship between the two papers exists.
        # If it does, delete it before adding a new relationship.
        edges = PaperRelationshipType(paper_from=paper_from, paper_to=paper_to)
        if edges:
            # Found existing relationship so remove it.
            paper_from.papers.remove(paper_to)

        # We have the two Paper objects.
        # Add the relationship between them.
        link_type = request.session["link_type"]
        edge = PaperRelationshipType(
            paper_from=paper_from, paper_to=paper_to, relationship_type=link_type
        )
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
            papers_found = Paper.objects.annotate(search=SearchVector("title")).filter(
                search=SearchQuery(paper_title_query, search_type="plain")
            )

            paper_relationship = form.cleaned_data["paper_connection"]

            if papers_found.count() > 0:  # found more than one matching papers
                for paper in papers_found:
                    print("\t{}".format(paper.title))

                    paper_connect_urls = [
                        reverse(
                            "paper_connect_paper_selected",
                            kwargs={"id": id, "pid": paper.id},
                        )
                        for paper in papers_found
                    ]

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

            datasets_found = Dataset.objects.annotate(
                search=SearchVector("keywords", "name")
            ).filter(search=SearchQuery(dataset_query_keywords, search_type="plain"))

            if datasets_found is not None:  # found more than one matching dataset
                # print("Found {} datasets that match".format(datasets_found.count()))
                # for dataset in datasets_found:
                #     print("\t{}".format(dataset.name))

                if datasets_found.count() > 0:
                    # for rid in relationship_ids:
                    datasets_connect_urls = [
                        reverse(
                            "paper_connect_dataset_selected",
                            kwargs={"id": id, "did": dataset.id},
                        )
                        for dataset in datasets_found
                    ]
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
            codes_found = Code.objects.annotate(search=SearchVector("keywords")).filter(
                search=SearchQuery(keywords, search_type="plain")
            )

            if codes_found is not None:
                # print("Found {} codes that match".format(codes_found.count()))
                # for code in codes_found:
                #     print("\t{} {}".format(code.website, code.keywords))

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
@staff_member_required
def paper_update(request, id):
    paper = get_object_or_404(Paper, pk=id)

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = PaperForm(request.POST)
        if form.is_valid():
            # ToDo: Check that the paper does not exist in the database
            #
            paper.title = form.cleaned_data["title"]
            paper.abstract = form.cleaned_data["abstract"]
            paper.keywords = form.cleaned_data["keywords"]
            paper.download_link = form.cleaned_data["download_link"]
            paper.is_public = True
            paper.save()

            return HttpResponseRedirect(reverse("papers_index"))
    # GET request
    else:
        form = PaperUpdateForm(
            initial={
                "title": paper.title,
                "abstract": paper.abstract,
                "keywords": paper.keywords,
                "download_link": paper.download_link,
                "is_public": True,
            }
        )

    return render(request, "paper_update.html", {"form": form, "paper": paper})


def _add_author(author, paper=None, order=1):
    """
    Adds author to the DB if author does not already exist and links to paper
    as author if paper is not None
    :param author <str>: Author name
    :param paper:
    """
    link_with_paper = False

    people_found = Person.objects.filter(name=author, )

    # print("**** People matching query {} ****".format(author))
    # print(people_found)

    if people_found.count() == 0:  # not in DB
        p = Person()
        p.name = author
        p.save()  # save to DB
        link_with_paper = True
    elif people_found.count() == 1:
        # Exactly one person found. Check if name is an exact match.
        p = people_found[0]
        # NOTE: The problem with this simple check is that if two people have
        # the same name then the wrong person will be linked to the paper.
        link_with_paper = True

    if link_with_paper and paper is not None:
        # link author with paper
        rel = PaperAuthorRelationshipData(paper=paper, author=p, order=order)
        rel.save()

@login_required
def paper_create_from_url(request):
    user = request.user
    if request.method == "POST":
        # get the data from arxiv
        url = request.POST["url"]
        validity, source_website, url = analysis_url(url)
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
        # Sometimes the title has new line characters that cause an JS error when drawing the
        # knowledge graph.
        # Strangely, the below does not work 
        # title = title.replace(r"\n","").replace(r"\r", "")
        # but the join below does!
        title = ' '.join(title.splitlines())
        print(f"title: {title}")
        if title is None or authors is None or abstract is None:
            print("missing information for paper")
            form = PaperImportForm()
            return render(
                request,
                "paper_form.html",
                {"form": form, "message": "Invalid source, please try again."},
            )

        # Add the paper in the database
        matching_papers = Paper.objects.filter(title=title, is_public=True)
        if matching_papers.count() > 0: # paper in DB already
            return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": matching_papers[0].id}))
        else:
            paper = Paper()
            paper.created_by = request.user
            paper.title = title
            paper.abstract = abstract
            paper.download_link = download_link
            paper.source_link = url
            paper.is_public = True
            paper.save()
            for order, paper_author in enumerate(authors.split(",")):
                _add_author(paper_author, paper, order+1)

            # Return user to paper detail page of newly added paper.
            return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": paper.id}))

        return HttpResponseRedirect(reverse("paper_create"))
    else:  # GET
        # request.session["from_external"] = False
        form = PaperImportForm()

    return render(request, "paper_form.html", {"form": form})


@login_required
def paper_flag_comment(request, id, cid):
    comment = get_object_or_404(Comment, pk=cid)

    # Check that the same user has not flagged the exact same comment already
    flagged = CommentFlag.objects.filter(proposed_by=request.user, comment=comment).all().count()

    if flagged == 0:
        # hasn't flagged this comment before
        # if this is POST request then process the Form data
        comment_flag = CommentFlag()
        if request.method == "POST":
            form = FlaggedCommentForm(request.POST)
            if form.is_valid():
                comment_flag.description = form.cleaned_data["description"]
                comment_flag.violation = form.cleaned_data["violation"]
                comment_flag.comment = comment
                comment_flag.proposed_by = request.user
                comment_flag.save()
                comment.is_flagged = True
                comment.save()

                data = {'is_valid': True}

                return JsonResponse(data)
            else:
                data = {'is_valid': False}

                return JsonResponse(data)
        # GET request
        else:
            form = FlaggedCommentForm()

            return render(request, "paper_flag_comment.html", {"form": form})

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


#
# Venue Views
#
def venues(request):
    all_venues = Venue.objects.all()[:100]

    message = None
    results_message = ''

    if request.method == "POST":
        form = SearchVenuesForm(request.POST)

        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            venue_name = form.cleaned_data["keywords"].lower()

            venues_found = Venue.objects.annotate(
                search=SearchVector("name", "keywords")
            ).filter(search=SearchQuery(venue_name, search_type="plain"))

            num_venues_found = len(venues_found)
            if venues_found:
                if num_venues_found > 25:
                    venues_found = venues_found[:25]
                    results_message = f"Showing 25 out of {num_venues_found} venues found. For best results, please narrow your search."
            else:
                results_message = "No results found. Please try again!"

            return render(
                    request,
                    "venue_results.html",
                    {"venues": venues_found, "form": form, "results_message": results_message},
                )

    if request.method == "GET":
        form = SearchVenuesForm()
        message = None

    return render(
        request, "venues.html", {"venues": all_venues, "form": form, "message": message}
    )


def venue_detail(request, id):
    papers_published_at_venue = None
    # Retrieve the paper from the database
    try:
        venue = Venue.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("venues_index"))

    request.session["last-viewed-venue"] = id
    return render(
        request, "venue_detail.html", {"venue": venue, "papers": venue.paper_set.all()}
    )


def venue_find(request):
    """
    Search for venue.
    :param request:
    :return:
    """
    keywords = request.GET.get("keywords", "")
    venues = Venue.objects.filter(name__icontains=keywords)

    return render(
        request,
        "venues.html",
        {"venues": venues},
    )


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
            other_venues = Venue.objects.filter(
                name__iexact=venue_name, publication_year=venue_year
            )
            if other_venues.count() == 0:
                form.save()
            # else:
            #     print(f"Found {other_venues.count()} matching venues.")
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
