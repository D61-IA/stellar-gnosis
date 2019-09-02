from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from catalog.models import Code
from catalog.forms import CodeForm
from catalog.forms import SearchCodesForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db


#
# Code Views
#
def codes(request):
    # all_codes = Code.nodes.all()
    all_codes = Code.nodes.order_by("-created")[:50]

    message = None
    if request.method == "POST":
        form = SearchCodesForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            keywords = form.cleaned_data["keywords"].lower()  # comma separated list

            codes = _code_find(keywords)

            if len(codes) > 0:
                return render(
                    request, "codes.html", {"codes": codes, "form": form, "message": ""}
                )
            else:
                message = "No results found. Please try again!"
    elif request.method == "GET":
        print("Received GET request")
        form = SearchCodesForm()

    return render(
        request, "codes.html", {"codes": all_codes, "form": form, "message": message}
    )


def code_detail(request, id):
    # Retrieve the paper from the database
    query = "MATCH (a:Code) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        # There should be only one result because ID should be unique. Here we check that at
        # least one result has been returned and take the first result as the correct match.
        # Now, it should not happen that len(results) > 1 since IDs are meant to be unique.
        # For the MVP we are going to ignore the latter case and just continue but ultimately,
        # we should be checking for > 1 and failing gracefully.
        all_codes = [Code.inflate(row[0]) for row in results]
        code = all_codes[0]
    else:  # go back to the paper index page
        return render(
            request,
            "codes.html",
            {"codes": Code.nodes.all(), "num_codes": len(Code.nodes.all())},
        )

    #
    # TO DO: Retrieve and list all papers that evaluate on this dataset.
    #

    request.session["last-viewed-code"] = id

    return render(request, "code_detail.html", {"code": code})


def _code_find(keywords):
    """
    Helper method for searching Neo4J DB for code repo.

    :param keywords: Dataset keywords search query
    :return:
    """
    code_keywords = [w for w in keywords.split()]
    codes = []
    if len(code_keywords) > 0:
        # Search using the keywords
        keyword_query = (
            "(?i).*" + "+.*".join("(" + w + ")" for w in code_keywords) + "+.*"
        )
        query = "MATCH (d:Code) WHERE d.keywords =~ { keyword_query} RETURN d LIMIT 25"
        results, meta = db.cypher_query(query, dict(keyword_query=keyword_query))
        if len(results) > 0:
            codes = [Code.inflate(row[0]) for row in results]

    return codes


def code_find(request):
    """
    Searching for a Code repo in the DB view.

    :param request:
    """
    message = None
    if request.method == "POST":
        form = SearchCodesForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            keywords = form.cleaned_data["keywords"].lower()  # comma separated list

            codes = _code_find(keywords)

            if len(codes) > 0:
                return render(
                    request,
                    "codes.html",
                    {"codes": codes, "form": form, "message": message},
                )
            else:
                message = "No results found. Please try again!"
    elif request.method == "GET":
        print("Received GET request")
        form = SearchCodesForm()

    return render(request, "code_find.html", {"form": form, "message": message})


@login_required
def code_create(request):
    user = request.user

    if request.method == "POST":
        code = Code()
        code.created_by = user.id
        form = CodeForm(instance=code, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("codes_index"))
    else:  # GET
        form = CodeForm()

    return render(request, "code_form.html", {"form": form})


@login_required
def code_update(request, id):
    # retrieve code node by ID
    # https://github.com/neo4j-contrib/neomodel/issues/199
    query = "MATCH (a:Code) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        codes = [Code.inflate(row[0]) for row in results]
        code = codes[0]
    else:
        code = Code()

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            code.keywords = form.cleaned_data["keywords"]
            code.description = form.cleaned_data["description"]
            code.website = form.cleaned_data["website"]
            code.save()

            return HttpResponseRedirect(reverse("codes_index"))
    # GET request
    else:
        query = "MATCH (a:Code) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=id))
        if len(results) > 0:
            codes = [Code.inflate(row[0]) for row in results]
            code = codes[0]
        else:
            code = Code()

        form = CodeForm(
            initial={
                "keywords": code.keywords,
                "description": code.description,
                "website": code.website,
            }
        )

    return render(request, "code_update.html", {"form": form, "code": code})


# should limit access to admin users only!!
@staff_member_required
def code_delete(request, id):
    print("WARNING: Deleting code repo id {} and all related edges".format(id))

    # Cypher query to delete the paper node
    query = "MATCH (c:Code) WHERE ID(c)={id} DETACH DELETE c"
    results, meta = db.cypher_query(query, dict(id=id))

    return HttpResponseRedirect(reverse("codes_index"))
