from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from catalog.models import Paper
from notes.forms import NoteForm
from notes.models import Note

# from catalog.forms import (NoteForm)

from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db

from datetime import datetime


#
# Note Views
#
@login_required
def note_create(request):
    user = request.user

    # Retrieve paper using paper id
    paper_id = request.session["last-viewed-paper"]
    query = "MATCH (a:Paper) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=paper_id))
    if len(results) > 0:
        all_papers = [Paper.inflate(row[0]) for row in results]
        paper = all_papers[0]
    else:  # just send him to the list of papers
        return HttpResponseRedirect(reverse("papers_index"))

    if request.method == "POST":
        note = Note()
        note.created_by = user
        note.paper_id = paper_id
        note.created_at = datetime.now()
        form = NoteForm(instance=note, data=request.POST)
        if form.is_valid():
            # add link from new comment to paper
            form.save()
            del request.session["last-viewed-paper"]
            return redirect("paper_detail", id=paper_id)
    else:  # GET
        form = NoteForm()

    return render(request, "notes/note_create.html", {"form": form})


@login_required
def note_update(request, id):
    note = Note.objects.filter(id=id).first()
    paper_id = request.session["last-viewed-paper"]
    # if this is POST request then process the Form data
    if request.method == "POST" and request.user == note.created_by:
        form = NoteForm(request.POST)
        if form.is_valid():
            note.note_content = form.cleaned_data["note_content"]
            note.save()
            del request.session["last-viewed-paper"]
            return redirect("paper_detail", id=paper_id)

    # GET request
    else:
        form = NoteForm(
            initial={"note_content": note.note_content, "updated_at": note.updated_at}
        )

    return render(request, "notes/note_update.html", {"form": form, "note": note})


@login_required()
def note_delete(request, id):
    note = Note.objects.filter(id=id).first()
    paper_id = request.session["last-viewed-paper"]
    if request.user == note.created_by:
        note.delete()
        del request.session["last-viewed-paper"]
    return redirect("paper_detail", id=paper_id)


@login_required
def note_index(request):
    notes = []
    notes_info = []
    if request.user.is_authenticated:
        notes = Note.objects.filter(created_by=request.user).order_by('-updated_at')
        for note in notes:
            print(note.note_content)
            paper_id = note.paper_id
            print("Paper id are: ", paper_id)
            query = "MATCH (p:Paper) where id(p) = {paper_id} RETURN p"
            results, meta = db.cypher_query(query, dict(paper_id=paper_id))
            if len(results) > 0:
                all_papers = [Paper.inflate(row[0]) for row in results]
                paper = all_papers[0]
                pairs = (note, paper)
                notes_info += [pairs]
    num_notes = len(notes)

    return render(request, "notes/note_index.html", {"notes": notes, "num_notes": num_notes, "notes_info": notes_info}, )
