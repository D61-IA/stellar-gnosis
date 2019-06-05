from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from catalog.models import ReadingGroup, ReadingGroupEntry
from django.urls import reverse
from django.http import HttpResponseRedirect
from catalog.forms import GroupForm, GroupEntryForm


def groups(request):

    all_groups = ReadingGroup.objects.all()

    message = None

    return render(
        request, "groups.html", {"groups": all_groups, "message": message}
    )


def group_detail(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)
    papers_proposed = group.papers.filter(date_discussed=None).order_by('-date_proposed')
    papers_discussed = group.papers.exclude(date_discussed=None).order_by('-date_discussed')

    print(papers_proposed)
    print(papers_discussed)

    return render(request, "group_detail.html", {"group": group,
                                                 "papers_proposed": papers_proposed,
                                                 "papers_discussed": papers_discussed})


@login_required
def group_create(request):
    user = request.user

    if request.method == "POST":
        group = ReadingGroup()
        group.owner = user
        form = GroupForm(instance=group, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("groups_index"))
    else:  # GET
        form = GroupForm()

    return render(request, "group_update.html", {"form": form})


@login_required
def group_update(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)
    # if this is POST request then process the Form data
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group.name = form.cleaned_data["name"]
            group.keywords = form.cleaned_data["keywords"]
            group.description = form.cleaned_data["description"]
            group.save()

            return HttpResponseRedirect(reverse("groups_index"))
    # GET request
    else:
        form = GroupForm(
            initial={
                "name": group.name,
                "keywords": group.keywords,
                "description": group.description,
            }
        )

    return render(request, "group_update.html", {"form": form, "group": group})


@login_required
def group_entry_remove(request, id, eid):

    group = get_object_or_404(ReadingGroup, pk=id)

    # Only the owner of a group can delete entries.
    if group.owner.id == request.user.id:
        group_entry = get_object_or_404(ReadingGroupEntry, pk=eid)
        group_entry.delete()

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))

@login_required
def group_entry_update(request, id, eid):

    group = get_object_or_404(ReadingGroup, pk=id)
    group_entry = get_object_or_404(ReadingGroupEntry, pk=eid)

    if request.user.id == group.owner.id:
        # if this is POST request then process the Form data
        if request.method == "POST":
            form = GroupEntryForm(request.POST)
            if form.is_valid():
                group_entry.date_discussed = form.cleaned_data["date_discussed"]
                print("Date to be discussed {}".format(group_entry.date_discussed))
                group_entry.save()

                return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))
        # GET request
        else:
            form = GroupEntryForm(
                initial={
                    "date_discussed": group_entry.date_discussed,
                }
            )
    else:
        print("You are not the owner.")
        return HttpResponseRedirect(reverse("groups_index"))

    return render(request, "group_entry_update.html", {"form": form,
                                                       "group": group,
                                                       "group_entry": group_entry})

# should limit access to admin users only!!
@staff_member_required
def group_delete(request, id):
    print("WARNING: Deleting code repo id {} and all related edges".format(id))
