from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from catalog.models import Code
from catalog.forms import CodeForm
from catalog.forms import SearchCodesForm

from django.urls import reverse
from django.http import HttpResponseRedirect


#
# Code Views
#
def codes(request):
    all_codes = Code.objects.all()[:100]

    message = None
    results_message = ""

    if request.method == "POST":
        form = SearchCodesForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            keywords = form.cleaned_data["keywords"].lower()  # comma separated list
            print(f"Searching for code using keywords {keywords}")

            codes = Code.objects.annotate(search=SearchVector("keywords")).filter(
                search=SearchQuery(keywords, search_type="plain")
            )

            num_codes_found = len(codes)
            if codes:
                if num_codes_found > 25:
                    codes = codes[:25]
                    results_message = f"Showing 25 out of {num_codes_found} codes found. For best results, please narrow your search."
            else:
                results_message = "No results found. Please try again!"

            return render(
                request,
                "code_results.html",
                {
                    "codes": codes,
                    "form": form,
                    "message": "",
                    "results_message": results_message,
                },
            )

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
    # request.session["last-viewed-code"] = id

    return render(
        request, "code_detail.html", {"code": code, "papers": code.papers.all()}
    )


def code_find(request):
    """
    Searching for a Code repo in the DB view.

    :param request:
    """
    keywords = request.GET.get("keywords", "")
    codes = Code.objects.filter(name__icontains=keywords)

    return render(
        request,
        "codes.html",
        {"codes": codes},
    )


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
            code.name = form.cleaned_data["name"]
            code.keywords = form.cleaned_data["keywords"]
            code.description = form.cleaned_data["description"]
            code.website = form.cleaned_data["website"]
            code.save()

            return HttpResponseRedirect(reverse("codes_index"))
    # GET request
    else:
        form = CodeForm(
            initial={
                "name": code.name,
                "keywords": code.keywords,
                "description": code.description,
                "website": code.website,
            }
        )

    return render(request, "code_update.html", {"form": form, "code": code})


@staff_member_required
def code_delete(request, id):
    print("WARNING: Deleting code repo id {} and all related edges".format(id))

    code = get_object_or_404(Code, pk=id)
    code.delete()

    return HttpResponseRedirect(reverse("codes_index"))
