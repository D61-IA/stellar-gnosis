from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from catalog.models import Code
from catalog.forms import CodeForm
from catalog.forms import SearchCodesForm

from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse


#
# Code Views
#
def codes(request):
    all_codes = Code.objects.all()

    message = None

    if request.method == 'POST':
        form = SearchCodesForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            keywords = form.cleaned_data["keywords"].lower()  # comma separated list
            print(f"Searching for code using keywords {keywords}")

            codes = Code.objects.annotate(
                search=SearchVector('keywords')
            ).filter(search=SearchQuery(keywords, search_type='plain'))

            print(codes)

            if codes:
                return render(request, "codes.html", {"codes": codes, "form": form, "message": ""})
            else:
                message = "No results found. Please try again!"

        print(message);

    elif request.method == "GET":
        print("Received GET request")
        form = SearchCodesForm()

    return render(
        request, "codes.html", {"codes": all_codes, "form": form, "message": message}
    )


def code_detail(request, id):
    # Retrieve the paper from the database
    try:
        code = Code.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("codes_index"))

    #
    # TO DO: Retrieve and list all papers that evaluate on this dataset.
    #
    request.session["last-viewed-code"] = id

    return render(request, "code_detail.html", {"code": code, "papers": code.papers.all()})


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
            print(f"Searching for code using keywords {keywords}")

            codes = Code.objects.annotate(
                search=SearchVector('keywords')
            ).filter(search=SearchQuery(keywords, search_type='plain'))

            print(codes)

            if codes:
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
    if request.method == "POST":
        code = Code()
        code.created_by = request.user
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
    try:
        code = Code.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("codes_index"))

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
        form = CodeForm(
            initial={
                "keywords": code.keywords,
                "description": code.description,
                "website": code.website,
            }
        )

    return render(request, "code_update.html", {"form": form, "code": code})


@staff_member_required
def code_delete(request, id):
    print("WARNING: Deleting code repo id {} and all related edges".format(id))

    try:
        code = Code.objects.get(pk=id)
        code.delete()
    except ObjectDoesNotExist:
        print(f"Code object with id={id} not found. Redirecting to code index page.")

    return HttpResponseRedirect(reverse("codes_index"))
