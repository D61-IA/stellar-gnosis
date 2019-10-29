from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse

from catalog.forms import FlaggedCommentForm
from catalog.models import CommentFlag


# creates a comment flag
# handles ajax POST requests
def cflag_create(request, comment_id):
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


# deletes the comment flag
# handles ajax GET requests
def cflag_remove(request, comment_id):
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
