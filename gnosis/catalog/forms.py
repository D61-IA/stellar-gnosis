from django import forms
from django.forms import ModelForm, Form
from .models import Paper, Person, Dataset, Venue, Comment, Code


#
# Search forms
#
class SearchVenuesForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_venue_name(self):
        return self.cleaned_data["venue_name"]

    def clean_venue_publication_year(self):
        return self.cleaned_data["venue_publication_year"]

    venue_name = forms.CharField(required=True)
    venue_publication_year = forms.CharField(required=True)


class SearchDatasetsForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

        self.fields["name"].label = "Name"
        self.fields[
            "keywords"
        ].label = "Keyword (single keyword, e.g. network, computer vision)"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    # one of them is required but we are going to enforce this in the
    # view code because we don't know at this stage which one of the
    # two the user will specify and we want to give her the option to
    # search by dataset name or keywords or both.
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={"size": 20}))
    keywords = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"size": 40})
    )


class SearchPapersForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_paper_title(self):
        return self.cleaned_data["paper_title"]

    paper_title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"size": 60})
    )


class SearchPeopleForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_person_name(self):
        return self.cleaned_data["person_name"]

    person_name = forms.CharField(required=True)


class SearchCodesForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

        self.fields["keywords"].label = "Keywords (e.g. GCN, network, computer vision)"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    keywords = forms.CharField(required=False)


#
# Model forms
#
class PaperForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["abstract"].widget = forms.Textarea()
        self.fields["abstract"].widget.attrs.update({"rows": "8"})
        self.fields["title"].label = "Title*"
        self.fields["abstract"].label = "Abstract*"
        self.fields["keywords"].label = "Keywords"
        self.fields["download_link"].label = "Download Link*"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_title(self):
        return self.cleaned_data["title"]

    def clean_abstract(self):
        return self.cleaned_data["abstract"]

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_download_link(self):
        return self.cleaned_data["download_link"]

    class Meta:
        model = Paper
        fields = ["title", "abstract", "keywords", "download_link"]


class PaperImportForm(Form):
    """
    A form for importing a paper from a website such as arXiv.org.
    The form only present the user with a field to enter a url.
    """

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_url(self):
        return self.cleaned_data["url"]

    url = forms.CharField(
        label="Source URL, e.g., https://arxiv.org/abs/1607.00653*",
        max_length=200,
        widget=forms.TextInput(attrs={"size": 60}),
    )


class PersonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["first_name"].label = "First Name*"
        self.fields["middle_name"].label = "Middle Name"
        self.fields["last_name"].label = "Last Name*"
        self.fields["affiliation"].label = "Affiliation"
        self.fields["website"].label = "Website"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})
            print(visible.field.widget.attrs.items())

    def clean_first_name(self):
        return self.cleaned_data["first_name"]

    def clean_middle_name(self):
        return self.cleaned_data["middle_name"]

    def clean_last_name(self):
        return self.cleaned_data["last_name"]

    def clean_affiliation(self):
        return self.cleaned_data["affiliation"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Person
        fields = ["first_name", "middle_name", "last_name", "affiliation", "website"]


class DatasetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # The default for the description field widget is text input. Buy we want to display
        # more than one rows so we replace it with a Textarea widget.
        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})

        self.fields["name"].label = "Name*"
        self.fields["keywords"].label = "Keywords*"
        self.fields["description"].label = "Description*"
        self.fields["source_type"].label = "Type*"
        self.fields["publication_date"].label = "Publication Date (yyyy-mm-dd)"
        self.fields["website"].label = "Website"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})

        print(type(self.fields["description"].widget))
        print(self.fields["description"].widget.attrs.items())

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_source_type(self):
        return self.cleaned_data["source_type"]

    def clean_publication_date(self):
        return self.cleaned_data["publication_date"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Dataset
        fields = [
            "name",
            "keywords",
            "description",
            "source_type",
            "publication_date",
            "website",
        ]


class VenueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["name"].label = "Name*"
        self.fields["publisher"].label = "Publisher*"
        # self.fields['publication_date'].help_text = 'YYYY-MM-DD'
        self.fields["publication_date"].label = "Publication Date (yyyy-mm-dd)*"
        self.fields["type"].label = "Type*"
        self.fields["peer_reviewed"].label = "Peer Reviewed*"
        self.fields["keywords"].label = "Keywords*"
        self.fields["website"].label = "Website"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})
            print(visible.field.widget.attrs.items())

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_publisher(self):
        return self.cleaned_data["publisher"]

    def clean_publication_date(self):
        return self.cleaned_data["publication_date"]

    def clean_type(self):
        return self.cleaned_data["type"]

    def clean_peer_reviewed(self):
        return self.cleaned_data["peer_reviewed"]

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Venue
        fields = [
            "name",
            "publisher",
            "publication_date",
            "type",
            "peer_reviewed",
            "keywords",
            "website",
        ]


class CommentForm(ModelForm):
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
        model = Comment
        fields = ["text"]


class CodeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # The default for the description field widget is text input. Buy we want to display
        # more than one rows so we replace it with a Textarea widget.
        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})

        self.fields["website"].label = "Website*"
        self.fields["keywords"].label = "Keywords*"
        self.fields["description"].label = "Description*"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})

        # print(type(self.fields['description'].widget))
        # print(self.fields['description'].widget.attrs.items())

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Code
        fields = ["website", "keywords", "description"]
