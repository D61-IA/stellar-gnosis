from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Paper
from notes.forms import NoteForm
from notes.models import Note

# from catalog.forms import (NoteForm)

from django.urls import reverse
from django.http import HttpResponseRedirect

from datetime import datetime

#
# Note Views
#
@login_required
def note_update(request, id):
    note = get_object_or_404(Note, pk=id)
    
    # if this is POST request then process the Form data
    if request.method == "POST" and request.user == note.created_by:
        form = NoteForm(request.POST)
        if form.is_valid():
            note.note_content = form.cleaned_data["note_content"]
            note.save()
            return redirect("paper_detail", id=note.paper.id)
    # GET request
    else:
        form = NoteForm(
            initial={"note_content": note.note_content, "updated_at": note.updated_at}
        )

    return render(request, "notes/note_update.html", {"form": form, "note": note})


@login_required()
def note_delete(request, id):

    note = get_object_or_404(Note, pk=id)
    paper_id = note.paper.id
    
    if request.user == note.created_by:
        note.delete()

    return redirect("paper_detail", id=paper_id)


@login_required
def note_index(request):
    notes_info = []
    
    notes = Note.objects.filter(created_by=request.user).order_by('-updated_at')

    for note in notes:
        print(note.note_content)
        paper_id = note.paper.id
        notes_info += [(note, note.paper)]
        print("Paper id are: ", paper_id)
            

    num_notes = notes.count()

    return render(request, "notes/note_index.html", {"notes": notes, "num_notes": num_notes, "notes_info": notes_info}, )
