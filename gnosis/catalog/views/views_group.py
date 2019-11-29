from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from catalog.models import ReadingGroup, ReadingGroupEntry, ReadingGroupMember
from django.urls import reverse
from django.http import HttpResponseRedirect
from catalog.forms import GroupForm, GroupEntryForm
from django.contrib.auth.models import User
from datetime import date
from itertools import chain


def groups(request):
    """Groups index view."""
    my_groups = []
    all_groups = ReadingGroup.objects.all().order_by("-created_at")[:50]
    if request.user.is_authenticated:
        my_groups = ReadingGroup.objects.filter(
            members__member=request.user, members__access_type="granted"
        ).all()
        my_groups_owned = ReadingGroup.objects.filter(owner=request.user).all()
        # Combine the Query sets
        my_groups = list(chain(my_groups, my_groups_owned))

    message = ""

    return render(
        request,
        "groups.html",
        {"groups": all_groups, "mygroups": my_groups, "message": message},
    )


@login_required
def group_manage_members(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)

    if group.owner == request.user:
        members = group.members.filter(access_type="granted").all()
        applicants = group.members.filter(access_type="requested").all()

        print(f"members: {members}")
        print(f"members: {applicants}")
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
            print(f"{request.user} joining public group.")
            member = ReadingGroupMember(member=request.user, access_type="granted")
            member.save()
            group.members.add(member)        
        else:
            print(f"{request.user} has status {member[0].access_type} for this group")
    else:
        # check if the user is already in the list of members
        if member.count() == 1:
            print(f"{request.user} requesting access to group.")
            member = ReadingGroupMember(member=request.user, access_type="requested")
            member.save()
            group.members.add(member)        
        else:
            print(f"{request.user} has status {member[0].access_type} for this group")

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


@login_required
def group_leave(request, id):
    group = get_object_or_404(ReadingGroup, pk=id)

    # if user is a member of the group then leave it.
    member = group.members.filter(member=request.user).all()
    # check if the user is already in the list of members
    if member.count() == 1:
        print("((( Leaving the group )))")
        member.delete()
    else:
        print("((( User is not a member of this group )))")

    return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))


def group_detail(request, id):

    group = get_object_or_404(ReadingGroup, pk=id)
    papers_proposed = group.papers.filter(date_discussed=None).order_by(
        "-date_proposed"
    )
    papers_discussed = group.papers.exclude(date_discussed=None).order_by(
        "-date_discussed"
    )

    print(papers_proposed)
    print(papers_discussed)

    today = date.today()

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
                group.videoconferencing = form.clean_videoconferencing()
                group.city = form.clean_city()
                group.country = form.clean_country()
                group.room = form.clean_room()
                group.day = form.clean_day()
                group.start_time = form.clean_start_time()
                group.end_time = form.clean_end_time()
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
                    "city": group.city,
                    "country": group.country,
                    "room": group.room,
                    "day": group.day,
                    "start_time": group.start_time,
                    "end_time": group.end_time,
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
                print("Date to be discussed {}".format(group_entry.date_discussed))
                group_entry.save()

                return HttpResponseRedirect(reverse("group_detail", kwargs={"id": id}))
        # GET request
        else:
            form = GroupEntryForm(
                initial={"date_discussed": group_entry.date_discussed}
            )
    else:
        print("You are not the owner.")
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
            print("Found group")
            group.delete()
            print("   ==> Deleted group.")
        else:
            print("Group does not belong to user.")

    return HttpResponseRedirect(reverse("groups_index"))
