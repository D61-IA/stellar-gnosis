from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from catalog.models import Dataset
from catalog.forms import DatasetForm
from catalog.forms import SearchDatasetsForm
from django.urls import reverse
from django.http import HttpResponseRedirect

#
# Dataset Views
#
def datasets(request):
    all_datasets = Dataset.objects.all()[:100]

    message = None
    results_message = ''
    if request.method == "POST":
        form = SearchDatasetsForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            keywords = form.cleaned_data[
                "keywords"
            ].lower()  # comma separated list

            datasets = Dataset.objects.annotate(
                search=SearchVector('keywords', 'name')
            ).filter(search=SearchQuery(keywords, search_type='plain'))

            num_datasets_found = len(datasets)           
            if datasets:
                if num_datasets_found > 25:
                    datasets = datasets[:25]
                    results_message = f"Showing 25 out of {num_datasets_found} datasets found. For best results, please narrow your search."
            else:
                results_message = "No results found. Please try again!"

            return render(
                    request,
                    "dataset_results.html",
                    {"datasets": datasets, "form": form, "results_message": results_message},
                )

    elif request.method == "GET":
        print("Received GET request")
        form = SearchDatasetsForm()

    return render(
        request,
        "datasets.html",
        {"datasets": all_datasets, "form": form, "message": message},
    )


def dataset_detail(request, id):
    # Retrieve the paper from the database

    dataset = get_object_or_404(Dataset, pk=id)

    # Retrieve and list all papers that evaluate on this dataset.
    papers = dataset.papers.all()  # the list of papers that evaluate on this dataset

    # request.session["last-viewed-dataset"] = id
    return render(request, "dataset_detail.html", {"dataset": dataset, "papers": papers})


def dataset_find(request):
    """
    Searching for a dataset in the DB.

    :param request:
    :return:
    """
    keywords = request.GET.get("keywords", "")
    datasets = Dataset.objects.filter(name__icontains=keywords)

    return render(
        request,
        "datasets.html",
        {"datasets": datasets},
    )


@login_required
def dataset_create(request):
    user = request.user

    if request.method == "POST":
        dataset = Dataset()
        dataset.created_by = user
        form = DatasetForm(instance=dataset, data=request.POST)
        if form.is_valid():
            other_datasets = Dataset.objects.filter(name__iexact=form.clean_name(),
                                                    publication_year=int(form.clean_publication_year()))
            if other_datasets.count() == 0:
                print("Found no other matching datasets")
                form.save()
            else:
                print(f"Found {other_datasets.count()} matching venues.")
            return HttpResponseRedirect(reverse("datasets_index"))
    else:  # GET
        form = DatasetForm()

    return render(request, "dataset_form.html", {"form": form})


# should limit access to admin users only!!
@staff_member_required
def dataset_delete(request, id):

    try:
        dataset = Dataset.objects.get(pk=id)
    except ObjectDoesNotExist:
        print(f"Could no find paper with id: {id}")
        return HttpResponseRedirect(reverse("datasets_index"))

    print("WARNING: Deleting dataset id {} and all related edges".format(id))
    dataset.delete()

    return HttpResponseRedirect(reverse("datasets_index"))


@login_required
def dataset_update(request, id):
    # retrieve paper by ID
    try:
        dataset = Dataset.objects.get(pk=id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse("datasets_index"))

    # if this is POST request then process the Form data
    if request.method == "POST":
        form = DatasetForm(request.POST)
        if form.is_valid():
            dataset.name = form.cleaned_data["name"]
            dataset.keywords = form.cleaned_data["keywords"]
            dataset.description = form.cleaned_data["description"]
            dataset.publication_year = form.cleaned_data["publication_year"]
            dataset.publication_month = form.cleaned_data["publication_month"]
            dataset.dataset_type = form.cleaned_data["dataset_type"]
            dataset.website = form.cleaned_data["website"]
            print(f"dataset.website: {dataset.website}")

            dataset.save()
            return HttpResponseRedirect(reverse("dataset_detail", kwargs={"id": id}))
    # GET request
    else:
        form = DatasetForm(
            initial={
                "name": dataset.name,
                "keywords": dataset.keywords,
                "description": dataset.description,
                "publication_year": dataset.publication_year,
                "publication_month": dataset.publication_month,
                "dataset_type": dataset.dataset_type,
                "website": dataset.website,
            }
        )

    return render(request, "dataset_update.html", {"form": form, "dataset": dataset})
