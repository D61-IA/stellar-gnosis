from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from catalog.forms import FlaggedCommentForm
from catalog.models import CommentFlag, Comment, PaperReport, Paper


def cflag_create(request, comment_id):
    """Creates a comment flag"""
    print("flag create ajax received!")
    user = request.user
    # if a flagging form is submitted
    if user.is_authenticated:

        flagged_comment = CommentFlag()
        flagged_comment.proposed_by = user

        form = FlaggedCommentForm(instance=flagged_comment, data=request.POST)

        # check if comment_id exists
        if comment_id is not None:
            flagged_comment.comment_id = comment_id
            is_valid = form.is_valid()

            # if the received request is ajax
            # return a json object for ajax requests containing form validity
            if is_valid:
                form.save()
            data = {'is_valid': is_valid}
            print("responded!")
            return JsonResponse(data)
    else:
        # handling unauthenticated post request.
        return HttpResponseBadRequest(reverse("paper_detail", kwargs={'id': id}))


def cflag_remove(request, comment_id):
    """Delets a comment flag"""
    print("flag remove ajax request received!")
    user = request.user
    data = {'is_successful': False}
    if user.is_authenticated:
        flag = user.comment_flags.get(comment_id=comment_id)
        num = flag.delete()
        # verify successful deletion
        if num[0] >= 0:
            data = {'is_successful': True}
            print("responded!")
            return JsonResponse(data)

        return JsonResponse(data)

    else:
        # handling unauthenticated get request.
        return HttpResponseBadRequest(reverse("paper_detail", kwargs={'id': id}))


@staff_member_required
def comment_restore(request, id):
    """It restores a flagged comment making it visible to users again."""
    comment = Comment.objects.get(pk=id)

    if request.method == 'POST':
        data = {'is_valid': False}
        if comment is not None:
            # Remove the entry from the CommentFlag table
            flags = CommentFlag.objects.filter(comment=comment).all()

            # Potentially (although not likely) more than one users may have flagged this comment. So, if we are restoring it,
            # then we delete all rows in the CommentFlag table.
            print(f"Found {flags.count()} flags for this comment.")

            for flag in flags:
                flag.delete()

            # reset is_flagged to False so users can see the comment in the paper detail
            comment.is_flagged = False
            comment.save()

            data['is_valid'] = True

        return JsonResponse(data)


@staff_member_required
def comment_delete(request, id):
    """Deletes a comment"""
    comment = Comment.objects.get(pk=id)
    # paper_id = comment.paper.id

    if request.method == 'POST':
        data = {'is_valid': False}
        if comment is not None:
            print(f"Warning: Deleting comment: {comment}")
            comment.delete()
            data['is_valid'] = True

        return JsonResponse(data)


@staff_member_required
def flagged_comments(request):
    """A view for all flagged comments that require moderation"""
    comments = CommentFlag.objects.all()

    return render(
        request,
        "flagged_comments.html",
        {"comments": comments},
    )


@staff_member_required
def reported_papers(request):
    """:return all reports"""
    reports = PaperReport.objects.all()

    return render(
        request,
        "reported_papers.html",
        {"reports": reports},
    )

@staff_member_required
def paper_report_delete(request, id):
    """Deletes a paper report."""
    if request.method == 'POST':
        report = PaperReport.objects.filter(id=id)
        data = {'is_valid': False}
        if report is not None:
            # Remove the entry from the CommentFlag table
            print(f"Warning: Deleting paper report: {report}")
            report.delete()
            data['is_valid'] = True

        return JsonResponse(data)


@staff_member_required
def paper_report_resolve(request, id):
    """Marks a report as resolved"""
    if request.method == 'POST':
        report = PaperReport.objects.get(id=id)
        data = {'is_resolved': ""}
        if report.is_resolved:
            report.is_resolved = False
            data['is_resolved'] = False
        else:
            report.is_resolved = True
            data['is_resolved'] = True

        report.save()

        return JsonResponse(data)
