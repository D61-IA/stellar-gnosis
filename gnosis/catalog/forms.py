from django import forms
from django.forms import ModelForm, Form
from .models import Paper, Person, Dataset, Venue, Comment, Code, CommentFlag
from .models import ReadingGroup, ReadingGroupEntry
from .models import Collection, CollectionEntry
from django.utils.safestring import mark_safe

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV2Invisible, ReCaptchaV3

from gnosis.settings import RECAPTCHA_PRIVATE_KEY_INV, RECAPTCHA_PUBLIC_KEY_INV, RECAPTCHA_PUBLIC_KEY_V3, RECAPTCHA_PRIVATE_KEY_V3


#
# Search forms
#

class SearchForm(Form):
    FILTER_CHOICES = (
        ('all', 'All'),
        ('papers', 'Papers'),
        ('people', 'People'),
        ('datasets', 'Datasets'),
        ('venues', 'Venues'),
        ('codes', 'Codes'),
    )

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_search_keywords(self):
        return self.cleaned_data["search_keywords"]

    search_keywords = forms.CharField(required=True)
    search_filter = forms.CharField(label='', widget=forms.Select(choices=FILTER_CHOICES))


class SearchAllForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
        #self.fields['search_type'].initial = 'all'

    def clean_search_type(self):
        return self.cleaned_data["search_type"]

    def clean_search_keywords(self):
        return self.cleaned_data["search_keywords"]

    SELECT_CHOICES = (
        ('all', 'All'),
        ('papers', 'Papers'),
        ('people', 'People'),
        ('venues', 'Venues'),
        ('datasets', 'Datasets'),
        ('codes', 'Codes'),
    )


    search_type = forms.ChoiceField(widget=forms.Select(), choices=SELECT_CHOICES, initial='all', required=True)
    search_keywords = forms.CharField(required=True)
    #search_type.initial = 'papers'
    def get_search_type(self):
        return self.search_type


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


class PaperConnectionForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_paper_title(self):
        return self.cleaned_data["paper_title"]

    def clean_paper_connection(self):
        return self.cleaned_data["paper_connection"]

    paper_title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"size": 60})
    )
    CHOICES = (('cites', 'cites'), ('uses', 'uses'), ('extends', 'extends'),)
    paper_connection = forms.ChoiceField(choices=CHOICES)


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
        # the label will now appear in two lines break at the br label
        # label= mark_safe("Source URL, e.g., https://arxiv.org/abs/1607.00653* <br /> Currently supported websites: arXiv.org, papers.nips.cc, www.jmlr.org/papers <br /> for papers from JMLR, please provide link of the abstract([abs]) page "),
        label=mark_safe("Source URL*"),
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
        self.fields['text'].widget.attrs.update({'id': 'comment_text'})

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:100%"})
            print(visible.field.widget.attrs.items())

    def clean_text(self):
        return self.cleaned_data["text"]

    def clean_publication_date(self):
        return self.cleaned_data["publication_date"]

    # def clean_author(self):
    #      return self.cleaned_data['author']

    # recaptcha checkbox, by default it uses checkbox keys at settings.py
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            attrs={
                'data-callback': 'dataCallback',
                'data-expired-callback': 'dataExpiredCallback',
                'data-error-callback': 'dataErrorCallback'
            }
        ),
        label=''
    )

    # recaptcha invisible
    # captcha = ReCaptchaField(
    #     public_key=RECAPTCHA_PUBLIC_KEY_INV,
    #     private_key=RECAPTCHA_PRIVATE_KEY_INV,
    #     widget=ReCaptchaV2Invisible,
    #     label=''
    # )

    # recaptcha v3
    # captcha = ReCaptchaField(
    #     public_key=RECAPTCHA_PUBLIC_KEY_V3,
    #     private_key=RECAPTCHA_PRIVATE_KEY_V3,
    #     widget=ReCaptchaV3(
    #         attrs={
    #             'required_score': 0.5,
    #         }
    #     ),
    #     label=''
    # )

    class Meta:
        model = Comment
        fields = ['text']


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


#
# SQL models
#
class GroupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # The default for the description field widget is text input. Buy we want to display
        # more than one rows so we replace it with a Textarea widget.
        self.fields["name"].widget = forms.Textarea()
        self.fields["name"].widget.attrs.update({"rows": "1"})

        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})

        self.fields["keywords"].label = "Keywords*"
        self.fields["description"].label = "Description*"
        self.fields["name"].label = "Name*"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_name(self):
        return self.cleaned_data["name"]

    class Meta:
        model = ReadingGroup
        fields = ["name", "description", "keywords"]


class GroupEntryForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # The default for the description field widget is text input. Buy we want to display
        # more than one rows so we replace it with a Textarea widget.
        self.fields["date_discussed"].widget = forms.DateInput()
        self.fields["date_discussed"].label = "Date (mm/dd/yyyy)"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})

    def clean_date_discussed(self):
        return self.cleaned_data["date_discussed"]

    class Meta:
        model = ReadingGroupEntry
        fields = ["date_discussed"]


#
# Collections
#
class CollectionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        # The default for the description field widget is text input. Buy we want to display
        # more than one rows so we replace it with a Textarea widget.
        self.fields["name"].widget = forms.Textarea()
        self.fields["name"].widget.attrs.update({"rows": "1"})

        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})

        self.fields["keywords"].label = "Keywords"
        self.fields["description"].label = "Description"
        self.fields["name"].label = "Name*"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs.update({"style": "width:25em"})

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_name(self):
        return self.cleaned_data["name"]

    class Meta:
        model = Collection
        fields = ["name", "description", "keywords"]


class FlaggedCommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        VIOLATION_CHOICES = [
            ('unwanted commercial content or spam', 'Unwanted commercial content or spam'),
            ('pornography or sexually explicit material', 'Pornography or sexually explicit material'),
            ('child abuse', 'Child abuse'),
            ('hate speech or graphic violence', 'Hate speech or graphic violence'),
            ('harassment or bullying', 'Harassment or bullying')
        ]

        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})
        self.fields["violation"] = forms.ChoiceField(choices=VIOLATION_CHOICES, widget=forms.RadioSelect())

        self.fields["description"].label = "Description"
        self.fields["violation"].label = "Violation"

    def clean_violation(self):
        return self.cleaned_data["violation"]

    def clean_description(self):
        return self.cleaned_data["description"]

    class Meta:
        model = CommentFlag
        fields = ['violation', 'description']