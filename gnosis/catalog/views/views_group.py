from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from catalog.models import ReadingGroup, ReadingGroupEntry
from django.urls import reverse
from django.http import HttpResponseRedirect
from catalog.forms import GroupForm, GroupEntryForm
from datetime import date


def groups(request):
    all_groups = ReadingGroup.objects.all().order_by('-created_at')
    message = ''

    return render(
        request, "groups.html", {"groups": all_groups, "message": message}
    )


def group_detail(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)
    papers_proposed = group.papers.filter(date_discussed=None).order_by('-date_proposed')
    papers_discussed = group.papers.exclude(date_discussed=None).order_by('-date_discussed')

    print(papers_proposed)
    print(papers_discussed)

    today = date.today()

    return render(request, "group_detail.html", {"group": group,
                                                 "papers_proposed": papers_proposed,
                                                 "papers_discussed": papers_discussed,
                                                 "today": today})


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

    if group.owner.id == request.user.id:
        # if this is POST request then process the Form data
        if request.method == "POST":
            form = GroupForm(request.POST)
            if form.is_valid():
                group.name = form.cleaned_data["name"]
                group.keywords = form.cleaned_data["keywords"]
                group.description = form.cleaned_data["description"]
                group.is_public = form.cleaned_data["is_public"]
                group.save()

                return HttpResponseRedirect(reverse("groups_index"))
        # GET request
        else:
            form = GroupForm(
                initial={
                    "name": group.name,
                    "keywords": group.keywords,
                    "description": group.description,
                    "is_public": group.is_public
                }
            )

        return render(request, "group_update.html", {"form": form, "group": group})

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


@login_required
def group_entry_remove(request, id, eid):

    group = get_object_or_404(ReadingGroup, pk=id)

    # Only the owner of a group can delete entries.
    if group.owner.id == request.user.id:
        group_entry = get_object_or_404(ReadingGroupEntry, pk=eid)
        group_entry.delete()

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


@login_required
def group_entry_unschedule(request, id, eid):

    group = get_object_or_404(ReadingGroup, pk=id)

    # Only the owner of a group can delete entries.
    if group.owner.id == request.user.id:
        group_entry = get_object_or_404(ReadingGroupEntry, pk=eid)
        group_entry.date_discussed = None
        group_entry.save()

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


#
@login_required
def group_delete(request, id):
    print("WARNING: Deleting group with id {}.".format(id))

    group = get_object_or_404(ReadingGroup, pk=id)
    if group:
        if group.owner == request.user:
            print("Found group")
            group.delete()
            print("   ==> Deleted group.")
        else:
            print("Group does not belong to user.")

    return HttpResponseRedirect(reverse("groups_index"))

