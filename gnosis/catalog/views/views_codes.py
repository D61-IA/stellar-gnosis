from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from catalog.models import Code, Paper, Person, Dataset, Venue
from catalog.forms import CodeForm
from catalog.forms import SearchCodesForm, SearchAllForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db

from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from neomodel import db
from datetime import date
from nltk.corpus import stopwords
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from django.contrib import messages
import re


#
# Code Views
#
def codes(request):
    # all_codes = Code.nodes.all()
    all_codes = Code.nodes.order_by("-created")[:50]

    form = SearchAllForm(request.POST)
    form.fields['search_type'].initial = 'codes'

    message = None
    paper_results = []
    person_results = []
    venue_results = []
    dataset_results = []
    codes_results = []

    if request.method == 'POST':

        print("Received POST request")
        if form.is_valid():
            english_stopwords = stopwords.words('english')
            search_filter = form.cleaned_data['search_type']
            search_keywords = form.cleaned_data['search_keywords'].lower()
            search_keywords_tokens = [w for w in search_keywords.split(' ') if not w in english_stopwords]

            all_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in search_keywords_tokens) + '+.*'
            query = "match (n) with n, [x in keys(n) WHERE n[x]=~ { all_query }] as doesMatch where size(doesMatch) > 0 return n"
            # query = "MATCH (p:Paper) WHERE  p.title =~ { paper_query } OR p.abstract =~ { paper_query }  RETURN p LIMIT 25"
            # print("Cypher query string {}".format(query))
            results, meta = db.cypher_query(query, dict(all_query=all_query))

            # print("Results: ", results)
            if len(results) > 0:

                if search_filter == 'all':
                    print("{} match(es) found ".format(len(results)))

                    for row in results:
                        for label in row[0].labels:

                            if label == 'Paper':
                                paper_results.append(Paper.inflate(row[0]))

                            elif label == 'Person':
                                person_results.append(Person.inflate(row[0]))
                                print(person_results)

                            elif label == 'Venue':
                                venue_results.append(Venue.inflate(row[0]))

                            elif label == 'Dataset':
                                dataset_results.append(Dataset.inflate(row[0]))

                            elif label == 'Code':
                                codes_results.append(Code.inflate(row[0]))

                    # papers = [Paper.inflate(row[0]) for row in results]
                    # search_results = paper_results.append(person_results.append(venue_results.append(
                    #   dataset_results.append(codes_results))))
                    print("Going to all results page..........")
                    return render(request, 'all_results.html', {'paper_results': paper_results,
                                                                'person_results': person_results,
                                                                'venue_results': venue_results,
                                                                'dataset_results': dataset_results,
                                                                'codes_results': codes_results,
                                                                'form': form, 'message': message})

                elif search_filter == 'papers':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Paper':
                                paper_results.append(Paper.inflate(row[0]))

                    if len(paper_results) > 0:
                        print("Found {} matching papers".format(len(paper_results)))
                        return render(request, "paper_results.html",
                                      {"paper_results": paper_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'codes.html', {'codes': all_codes, 'form': form,
                                                               'message': message})

                elif search_filter == 'people':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Person':
                                person_results.append(Person.inflate(row[0]))

                    if len(person_results) > 0:
                        print("Found {} matching papers".format(len(person_results)))
                        return render(request, "people_results.html",
                                      {"person_results": person_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'codes.html', {'venues': all_codes, 'form': form,
                                                               'message': message})

                elif search_filter == 'venues':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Venue':
                                venue_results.append(Venue.inflate(row[0]))

                    if len(venue_results) > 0:
                        print("Found {} matching papers".format(len(venue_results)))
                        return render(request, "venue_results.html",
                                      {"venue_results": venue_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'codes.html', {'venues': all_codes, 'form': form,
                                                               'message': message})

                elif search_filter == 'datasets':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Dataset':
                                dataset_results.append(Dataset.inflate(row[0]))

                    if len(dataset_results) > 0:
                        print("Found {} matching papers".format(len(dataset_results)))
                        return render(request, "dataset_results.html",
                                      {"dataset_results": dataset_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'codes.html', {'venues': all_codes, 'form': form,
                                                               'message': message})

                elif search_filter == 'codes':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Code':
                                codes_results.append(Code.inflate(row[0]))

                    if len(codes_results) > 0:
                        print("Found {} matching papers".format(len(codes_results)))
                        return render(request, "code_results.html",
                                      {"codes_results": codes_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'codes.html', {'codes': all_codes,
                                                               'form': form,
                                                               'message': message})



            else:
                message = "No results found. Please try again!"

        print(message);

    elif request.method == "GET":
        print("Received GET request")
        form = SearchAllForm()
        form.fields['search_type'].initial = 'codes'

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
