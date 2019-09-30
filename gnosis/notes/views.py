from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from catalog.models import Paper
from notes.forms import NoteForm
from notes.models import Note

# from catalog.forms import (NoteForm)

from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db


#
# Note Views
#
@login_required
def note_create(request):
    user = request.user

    # Retrieve paper using paper id
    paper_id = request.session["last-viewed-paper"]
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=paper_id))
    if len(results) > 0:
        all_papers = [Paper.inflate(row[0]) for row in results]
        paper = all_papers[0]
    else:  # just send him to the list of papers
        HttpResponseRedirect(reverse("papers_index"))

    if request.method == "POST":
        note = Note()
        note.author = user
        note.paper = paper.title
        form = NoteForm(instance=note, data=request.POST)
        if form.is_valid():
            # add link from new comment to paper
            form.save()
            del request.session["last-viewed-paper"]
            return redirect("paper_detail", id=paper_id)
    else:  # GET
        form = NoteForm()

    return render(request, "note_create.html", {"form": form})


@login_required
def note_update(request, id):
    note = Note.objects.filter(id=id).first()
    paper_id = request.session["last-viewed-paper"]
    # if this is POST request then process the Form data
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note.text = form.cleaned_data["text"]
            note.save()
            del request.session["last-viewed-paper"]
            return redirect("paper_detail", id=paper_id)

    # GET request
    else:
        form = NoteForm(
            initial={"text": note.text, "date_posted": note.date_posted}
        )

    return render(request, "note_update.html", {"form": form, "note": note})


@login_required()
def note_delete(request, id):
    note = Note.objects.filter(id=id).first()
    paper_id = request.session["last-viewed-paper"]
    note.delete()
    del request.session["last-viewed-paper"]
    return redirect("paper_detail", id=paper_id)