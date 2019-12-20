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

            if papers:
                return render(
                    request,
                    "paper_results.html",
                    {"papers": papers, "form": form, "message": ""},
                )
            else:
                message = "No results found. Please try again!"
                messages.add_message(request, messages.INFO, message)        

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
    # ToDo: Improve this code to correctly handle middle names that are more than one word.
    authors_set = PaperAuthorRelationshipData.objects.filter(paper=paper).order_by('order')
    print(f"** Retrieved authors {authors_set}")

    authors = []
    for author in authors_set:
        author = author.author
        author_name = str(author)  # author.first_name[0]+'. '+author.middle_name
        author_name = author_name.split()
        if len(author_name) > 2:
            authors.append(
                author_name[0][0] + ". " + author_name[1][0] + ". " + author_name[2]
            )
        else:
            authors.append(author_name[0][0] + ". " + author_name[1])
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

    print(f"papers_out: {papers_out}")
    print(f"paper_in: {papers_in}")

    # Sort nodes and store them in arrays accordingly
    # 'out' refers to being from the paper to the object
    # line property for out
    line = "solid"
    for paper_out in papers_out:
        paper=paper_out.paper_to
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
    author_str = ", {{data : {{id: '{}', first_name: '{}', middle_name: '{}', last_name: '{}', href: '{}', type: '{}', label: '{}'}} }}"
    # query for everything that points to the paper
    paper_authors = main_paper.person_set.all()
    print(f"paper authors {paper_authors}")

    line = "dashed"
    for author in paper_authors:
        # reformat middle name from string "['mn1', 'mn2', ...]" to array ['mn1', 'mn2', ...]
        middle_name = ""
        if author.middle_name is not None:
            middle_name = author.middle_name.replace("'", r"\'")
            middle_name = middle_name.replace("[", r"")
            middle_name = middle_name.replace("]", r"")

        ego_json += author_str.format(
            author.id + offset,
            author.first_name,
            middle_name,
            author.last_name,
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

    node_temp = (
        ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"
    )
    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    venue = main_paper.was_published_at

    if venue:
        ego_json += node_temp.format(venue.id+offset,
                                     venue.name,
                                     reverse("venue_detail", kwargs={"id": venue.id}),
                                     'Venue', 'was published at')

        ego_json += rela_temp.format(main_paper.id,
                                     '-',
                                     venue.id+offset,
                                     'Venue',
                                     'was published at',
                                     main_paper.id,
                                     venue.id+offset,
                                     'solid')

    return ego_json


def _get_paper_dataset_network(main_paper, ego_json, offset=150):

    node_temp = (
        ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"
    )
    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    datasets = main_paper.dataset_set.all()
    print(f"Paper {main_paper} evaluates on datasets {datasets}.")

    for dataset in datasets:
        ego_json += node_temp.format(dataset.id+offset,
                                     dataset.name,
                                     reverse("dataset_detail", kwargs={"id": dataset.id}),
                                     'Dataset',
                                     'evaluates on')

        ego_json += rela_temp.format(main_paper.id,
                                     '-',
                                     dataset.id+offset,
                                     'Dataset',
                                     'evaluates on',
                                     main_paper.id,
                                     dataset.id+offset, 'solid')

    return ego_json


def _get_paper_code_network(main_paper, ego_json, offset=200):

    node_temp = (
        ", {{data : {{id: '{}', title: '{}', href: '{}', type: '{}', label: '{}' }}}}"
    )
    rela_temp = ",{{data: {{ id: '{}{}{}', type: '{}', label: '{}', source: '{}', target: '{}', line: '{}' }}}}"

    codes = main_paper.code_set.all()

    for code in codes:
        ego_json += node_temp.format(code.id+offset,
                                     'Code',
                                     reverse("code_detail", kwargs={"id": code.id}),
                                     'Code',
                                     'implements')
        ego_json += rela_temp.format(main_paper.id,
                                     '-',
                                     code.id+offset,
                                     'Code',
                                     'implements',
                                     code.id+offset,
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
                return render(
                    request,
                    "papers_index.html",
                    {"papers": papers, "form": form, "message": message},
                )
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
    print("\n===============================================")
    print(f"In paper_add_note for paper with id={id}")
    print("\n===============================================")

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
    try:
        paper = Paper.objects.get(pk=id)
        group = ReadingGroup.objects.get(pk=gid)
    except ObjectDoesNotExist:
        return Http404

    print("Found group {}".format(group))
    # Check if the user has permission to propose a paper for this group.
    # If group is public then all good.
    # If the group is private then check if user is a member of this group.
    q_set = group.members.filter(member=request.user).all()
    if group.owner==request.user or group.is_public or (q_set.count()==1 and q_set[0].access_type=='granted'):
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
    else:
        print("You don't have permission to propose papers for this group.")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


@login_required
def paper_add_to_group(request, id):
    message = None
    # Get all reading groups that this person has created

    # The public reading groups
    groups = ReadingGroup.objects.filter(is_public=True).all()
    # The private reading groups the user has been granted access to.
    # This excludes the user who owns/created the group!
    groups_private = ReadingGroup.objects.filter(is_public=False, members__member=request.user, members__access_type='granted')
    groups_owner = ReadingGroup.objects.filter(is_public=False, owner=request.user)
    # Combine the Query sets
    groups = list(chain(groups, groups_owner, groups_private))

    group_urls = [
        reverse("paper_add_to_group_selected", kwargs={"id": id, "gid": group.id})
        for group in groups
    ]

    all_groups = zip(groups, group_urls)

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
                search=SearchVector("first_name", "last_name", "middle_name")
            ).filter(search=SearchQuery(name, search_type="plain"))

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
    
    if paper_from == paper_to:
        messages.add_message(request, messages.INFO, "You cannot connect a paper with itself.")
    else:
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
        link_type = request.session["link_type"]
        print(f"link_type: {link_type}")
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
            print(f"Searching for paper using keywords {paper_title_query}")
            papers_found = Paper.objects.annotate(search=SearchVector("title")).filter(
                search=SearchQuery(paper_title_query, search_type="plain")
            )
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
                search=SearchVector("keywords", "name")
            ).filter(search=SearchQuery(dataset_query_keywords, search_type="plain"))

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
            codes_found = Code.objects.annotate(search=SearchVector("keywords")).filter(
                search=SearchQuery(keywords, search_type="plain")
            )

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
    author_name = author.strip().split(" ")

    if len(author_name) > 2:
        people_found = Person.objects.filter(
            first_name=author_name[0],
            middle_name=author_name[1],
            last_name=author_name[2],
        )
    else:
        people_found = Person.objects.filter(
            first_name=author_name[0], last_name=author_name[1]
        )

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
        rel = PaperAuthorRelationshipData(paper=paper, author=p, order=order)
        rel.save()


@login_required
def paper_create(request):
    user = request.user

    if request.method == "POST":
        print("   POST")
        paper = Paper()
        paper.created_by = user
        form = PaperForm(instance=paper, data=request.POST)
        if form.is_valid():
            # Check if the paper already exists in DB
            # Exact match on title.
            matching_papers = Paper.objects.filter(title=form.cleaned_data["title"], is_public=True)
   
            if matching_papers.count() > 0:  # paper in DB already
                message = "Paper already exists in Gnosis!"
                messages.add_message(request, messages.INFO, message)
                return HttpResponseRedirect(reverse("papers_index"))
            else:  # the paper is not in DB yet.
                form.save()  # store
                # Now, add the authors and link each author to the paper with an "authors"
                # type edge.
                if request.session.get("from_external", False):
                    paper_authors = request.session["external_authors"]
                    print(f"Received authors {paper_authors}")
                    for order, paper_author in enumerate(paper_authors.split(",")):
                        print("Adding author {}".format(paper_author))
                        print(f"** Adding author {paper_author} with order {order+1}")
                        _add_author(paper_author, paper, order+1)

                request.session["from_external"] = False  # reset
                # go back to paper index page.
                # Should this redirect to the page of the new paper just added?
                # return HttpResponseRedirect(reverse("papers_index"))
                return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": paper.id}))
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
            is_public = True

            form = PaperForm(
                initial={
                    "title": title,
                    "abstract": abstract,
                    "download_link": download_link,
                    "source_link": url,
                    "is_public": is_public
                }
            )
        else:
            form = PaperForm()

    return render(request, "paper_form.html", {"form": form})

@login_required
def paper_create_from_url(request):
    user = request.user
    if request.method == "POST":
        # create the paper from the extracted data and send to
        # paper_form.html asking the user to verify
        print("{}".format(request.POST["url"]))
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
        if title is None or authors is None or abstract is None:
            print("missing information for paper")
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


@login_required
def paper_flag_comment(request, id, cid):

    comment = get_object_or_404(Comment, pk=cid)

    # Check that the same user has not flagged the exact same comment already
    flagged = CommentFlag.objects.filter(proposed_by=request.user, comment=comment).all().count()

    if flagged == 0:
        # hasn't flagged this comment before
        # if this is POST request then process the Form data
        print("Comment has not been flagged before.")
        comment_flag = CommentFlag()
        if request.method == "POST":
            print("POST")
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
                print("responded!")
                return JsonResponse(data)
            else:
                data = {'is_valid': False}
                print("responded!")
                return JsonResponse(data)
        # GET request
        else:
            print("GET: new FlaggedCommentForm")
            form = FlaggedCommentForm()

            return render(request, "paper_flag_comment.html", {"form": form})

    return HttpResponseRedirect(reverse("paper_detail", kwargs={"id": id}))


#
# Venue Views
#
def venues(request):
    all_venues = Venue.objects.all()

    message = None

    if request.method == "POST":
        form = SearchVenuesForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            venue_name = form.cleaned_data["keywords"].lower()
            # venue_publication_year = form.cleaned_data["venue_publication_year"]

            print(f"Searching for venue using keywords {venue_name}")

            venues_found = Venue.objects.annotate(
                search=SearchVector("name", "keywords")
            ).filter(search=SearchQuery(venue_name, search_type="plain"))

            if venues_found.count() > 0:
                print("Found {} venues that match".format(venues_found.count()))
                return render(
                    request,
                    "venues.html",
                    {"venues": venues_found, "form": form, "message": message},
                )
            else:
                message = "No results found. Please try again!"

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

    print(f"Papers published at this venue {venue.paper_set.all()}")  

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
    message = None
    if request.method == "POST":
        form = SearchVenuesForm(request.POST)
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            venue_name = form.cleaned_data["venue_name"].lower()
            venue_publication_year = form.cleaned_data["venue_publication_year"]

            print(
                f"Searching for venue using keywords {venue_name} and year {venue_publication_year}"
            )

            venues_found = Venue.objects.annotate(
                search=SearchVector("name", "keywords")
            ).filter(search=SearchQuery(venue_name, search_type="plain"))

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
            other_venues = Venue.objects.filter(
                name__iexact=venue_name, publication_year=venue_year
            )
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
