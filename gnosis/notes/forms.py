from django import forms
from django.forms import ModelForm
from .models import Note


class NoteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["text"].widget = forms.Textarea()
        self.fields["text"].widget.attrs.update({"rows": "5"})
        self.fields["text"].label = ""

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:35em"})
            print(visible.field.widget.attrs.items())

    def clean_text(self):
        return self.cleaned_data["text"]

    def clean_publication_date(self):
        return self.cleaned_data["publication_date"]

    # def clean_author(self):
    #     return self.cleaned_data['author']

    class Meta:
        model = Note
        fields = ["text"]
