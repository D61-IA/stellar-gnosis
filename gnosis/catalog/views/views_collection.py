from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from catalog.models import Collection, CollectionEntry
from django.urls import reverse
from django.http import HttpResponseRedirect

from catalog.forms import CollectionForm


@login_required
def collections(request):

    all_collections = Collection.objects.filter(owner=request.user)

    message = None
    print("Collections view!")
    return render(
        request, "collections.html", {"collections": all_collections, "message": message}
    )


@login_required
def collection_detail(request, id):

    collection = get_object_or_404(Collection, pk=id)

    if collection.owner == request.user:
        papers = collection.papers.order_by('-created_at')
        print(papers)

        return render(request, "collection_detail.html", {"collection": collection,
                                                          "papers": papers, })

    return HttpResponseRedirect(reverse("collections"))


@login_required
def collection_create(request):
    user = request.user

    print("Creating a new collection")

    if request.method == "POST":
        collection = Collection()
        collection.owner = user
        form = CollectionForm(instance=collection, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("collections"))
    else:  # GET
        form = CollectionForm()

    return render(request, "collection_update.html", {"form": form})


@login_required
def collection_update(request, id):

    print("Creating/Updating collection with id: {}".format(id))

    collection = get_object_or_404(Collection, pk=id)
    # if this is POST request then process the Form data
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection.name = form.cleaned_data["name"]
            collection.keywords = form.cleaned_data["keywords"]
            collection.description = form.cleaned_data["description"]
            collection.save()

            return HttpResponseRedirect(reverse("collections"))
    # GET request
    else:
        form = CollectionForm(
            initial={
                "name": collection.name,
                "keywords": collection.keywords,
                "description": collection.description,
            }
        )

    return render(request, "collection_update.html", {"form": form, "collection": collection})


@login_required
def collection_entry_remove(request, id, eid):

    collection = get_object_or_404(Collection, pk=id)

    # Only the owner of a collection can delete entries.
    if collection.owner.id == request.user.id:
        c_entry = get_object_or_404(CollectionEntry, pk=eid)
        c_entry.delete()

    return HttpResponseRedirect(reverse("collection_detail", kwargs={"id": id}))


# should limit access to admin users only!!
# @staff_member_required
@login_required
def collection_delete(request, id):
    """Delete view"""
    print("WARNING: Deleting collection with id {}".format(id))

    collection = get_object_or_404(Collection, pk=id)
    if collection:
            if collection.owner == request.user:
                print("Found collection")
                collection.delete()
                print("   ==> Deleted collection.")
            else:
                print("Collection does not belong to user.")

    return HttpResponseRedirect(reverse("collections"))


@login_required
def collection_entry_remove(request, id, eid):
    """Delete view"""
    print("WARNING: Deleting collection entry with id {}".format(eid))

    collection = get_object_or_404(Collection, pk=id)
    if collection:
            if collection.owner == request.user:
                print("Found collection")
                c_entry = get_object_or_404(CollectionEntry, pk=eid)
                # c_entry = collection.papers.filter(id=eid)
                c_entry.delete()
                print("   ==> Deleted collection entry.")
                return HttpResponseRedirect(reverse("collection_detail", kwargs={"id": id}))
            else:
                print("Collection does not belong to user.")

    return HttpResponseRedirect(reverse("collections"))
