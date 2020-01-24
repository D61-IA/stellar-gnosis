from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.shortcuts import render, get_object_or_404
from catalog.models import ReadingGroup, ReadingGroupEntry, ReadingGroupMember
from django.urls import reverse
from django.http import HttpResponseRedirect
from catalog.forms import GroupForm, GroupEntryForm, SearchGroupsForm
from django.contrib.auth.models import User
from datetime import date
from datetime import datetime
from itertools import chain
from django.utils import timezone
import pytz

@login_required
def groups_user(request):
    """My Groups index view."""
    message = ""
    my_groups = []

    # First, we find all the groups the user is a member or owner
    my_groups = ReadingGroup.objects.filter(
        members__member=request.user, members__access_type="granted"
    ).all()
    my_groups_owned = ReadingGroup.objects.filter(owner=request.user).all()
    # Combine the Query sets
    my_groups = list(chain(my_groups, my_groups_owned))

    if request.method == 'POST':
        # user is searching for a group
        form = SearchGroupsForm(request.POST)
        if form.is_valid():
            query = form.clean_query()
            # print(f"Searching for groups using keywords {query}")
            all_groups = ReadingGroup.objects.annotate(
                 search=SearchVector('keywords')
            ).filter(search=SearchQuery(query, search_type='plain'))

            print(all_groups)

            if all_groups is None:
                message = "No results found. Please try again!"
            else:
                return render(
                    request,
                    "groups.html",
                    {"groups": all_groups, "message": message, "form": form },
                )

    elif request.method == "GET":
        form = SearchGroupsForm()

    return render(
        request,
        "groups_user.html",
        {"mygroups": my_groups, "message": message, "form": form, },
    )

def groups(request):
    """Groups index view."""
    message = ""
    all_groups = ReadingGroup.objects.all().order_by("-created_at")[:200]

    if request.method == 'POST':
        # user is searching for a group
        form = SearchGroupsForm(request.POST)
        if form.is_valid():
            query = form.clean_query()
            # print(f"Searching for groups using keywords {query}")
            all_groups = ReadingGroup.objects.annotate(
                 search=SearchVector('keywords')
            ).filter(search=SearchQuery(query, search_type='plain'))

            # print(all_groups)

            if all_groups is None:
                message = "No results found. Please try again!"

    elif request.method == "GET":
        form = SearchGroupsForm()

    return render(
        request,
        "groups.html",
        {"groups": all_groups, "message": message, "form": form },
    )


@login_required
def group_manage_members(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)

    if group.owner == request.user:
        members = group.members.filter(access_type="granted").all()
        applicants = group.members.filter(access_type="requested").all()

        # print(f"members: {members}")
        # print(f"members: {applicants}")
        return render(
            request,
            "group_manage_members.html",
            {
                "members": members,
                "applicants": applicants,
                # "is_public": group.is_public,
                "group": group,
            },
        )

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


@login_required
def group_grant_access(request, id, aid):

    group = get_object_or_404(ReadingGroup, pk=id)

    if group.owner == request.user:
        applicant = get_object_or_404(User, pk=aid)
        # How do we change the applicant's status?
        applicant_request_entry = group.members.filter(member=applicant).all()
        if applicant_request_entry.count() == 1:                        
            # I don't know if this is the best way to do this, but I will delete the existing entry
            # with access_type set to 'requested' and add a new one with access_type 'granted'.
            applicant_request_entry.delete()
            member = ReadingGroupMember(member=applicant, access_type="granted")
            member.save()
            group.members.add(member)

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


@login_required
def group_deny_access(request, id, aid):

    group = get_object_or_404(ReadingGroup, pk=id)

    if group.owner == request.user:
        applicant = get_object_or_404(User, pk=aid)
        applicant_request_entry = group.members.filter(member=applicant).all()
        if applicant_request_entry.count() == 1:                        
            applicant_request_entry.delete()
    
    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


@login_required
def group_join(request, id):
    group = get_object_or_404(ReadingGroup, pk=id)

    # If the group is public, then joining is automatic.
    # if user does not have access to the group and the group is private, request it so that the group
    # owner can grant or deny access.
    member = group.members.filter(member=request.user).all()
    if group.is_public:
        # check if the user is already in the list of members
        if member.count() == 0:
            # print(f"{request.user} joining public group.")
            member = ReadingGroupMember(member=request.user, access_type="granted")
            member.save()
            group.members.add(member)        
        # else:
        #     print(f"{request.user} has status {member[0].access_type} for this group")
    else:
        # check if the user is already in the list of members
        if member.count() == 0:
            # print(f"{request.user} requesting access to group.")
            member = ReadingGroupMember(member=request.user, access_type="requested")
            member.save()
            group.members.add(member)        
        # else:
        #     print(f"{request.user} has status {member[0].access_type} for this group")

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))

@login_required
def group_leave(request, id):
    group = get_object_or_404(ReadingGroup, pk=id)

    # if user is a member of the group then leave it.
    member = group.members.filter(member=request.user).all()
    # check if the user is already in the list of members
    if member.count() == 1:
        # print("((( Leaving the group )))")
        member.delete()
    # else:
    #     print("((( User is not a member of this group )))")

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


def group_detail(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)
    papers_proposed = group.papers.filter(date_discussed=None).order_by(
        "-date_proposed"
    )
    papers_discussed = group.papers.exclude(date_discussed=None).order_by(
        "-date_discussed"
    )

    # Get the current day on the group's timezone. The server is on UTC time so, we
    # ask for the current day and convert it to the group's timezone.
    today = timezone.now().astimezone(group.timezone).date()

    # Flag to indicate if the user is a member of this group, if the group is private
    is_member = False
    has_requested_access = False

    if not request.user.is_anonymous:
        member = group.members.filter(member=request.user).all()
        if member.count() == 1 :
            print(f"{request.user} has status {member[0].access_type} for this group")
            if member[0].access_type == 'granted':
                is_member = True
            elif member[0].access_type == 'requested':
                has_requested_access = True

    return render(
        request,
        "group_detail.html",
        {
            "group": group,
            "papers_proposed": papers_proposed,
            "papers_discussed": papers_discussed,
            "is_member": is_member,
            "has_requested_access": has_requested_access,
            "today": today,
        },
    )


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
                group.slack = form.clean_slack()
                group.telegram = form.clean_telegram()
                group.videoconferencing = form.clean_videoconferencing()
                group.address = form.clean_address()
                group.city = form.clean_city()
                group.country = form.clean_country()
                group.room = form.clean_room()
                group.day = form.clean_day()
                group.start_time = form.clean_start_time()
                group.end_time = form.clean_end_time()
                group.timezone = form.clean_timezone()
                group.save()

                return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))
        # GET request
        else:
            form = GroupForm(
                initial={
                    "name": group.name,
                    "keywords": group.keywords,
                    "description": group.description,
                    "is_public": group.is_public,
                    "address": group.address, 
                    "city": group.city,
                    "country": group.country,
                    "room": group.room,
                    "day": group.day,
                    "start_time": group.start_time,
                    "end_time": group.end_time,
                    "timezone": group.timezone,
                    "slack": group.slack,
                    "telegram": group.telegram,
                    "videoconferencing": group.videoconferencing,
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
                # print("Date to be discussed {}".format(group_entry.date_discussed))
                group_entry.save()

                return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))
        # GET request
        else:
            form = GroupEntryForm(
                initial={"date_discussed": group_entry.date_discussed}
            )
    else:
        # print("You are not the owner.")
        return HttpResponseRedirect(reverse("groups_index"))

    return render(
        request,
        "group_entry_update.html",
        {"form": form, "group": group, "group_entry": group_entry},
    )


#
@login_required
def group_delete(request, id):
    print("WARNING: Deleting group with id {}.".format(id))

    group = get_object_or_404(ReadingGroup, pk=id)
    if group:
        if group.owner == request.user:
            # print("Found group")
            group.delete()
            # print("   ==> Deleted group.")
        # else:
        #     print("Group does not belong to user.")

    return HttpResponseRedirect(reverse("groups_index"))
