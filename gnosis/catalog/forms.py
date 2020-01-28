from django import forms
from django.forms import ModelForm, Form
from .models import Paper, Person, Dataset, Venue, Comment, Code, CommentFlag, Profile, PaperReport
from .models import ReadingGroup, ReadingGroupEntry
from .models import Collection, CollectionEntry
from django.utils.safestring import mark_safe
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV2Invisible, ReCaptchaV3

from gnosis.settings import RECAPTCHA_PRIVATE_KEY_INV, RECAPTCHA_PUBLIC_KEY_INV, RECAPTCHA_PUBLIC_KEY_V3, \
    RECAPTCHA_PRIVATE_KEY_V3


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
        # self.fields['search_type'].initial = 'all'

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

    # search_type.initial = 'papers'
    def get_search_type(self):
        return self.search_type


class SearchVenuesForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    keywords = forms.CharField(required=True)


class SearchDatasetsForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    keywords = forms.CharField(required=True, )


class SearchGroupsForm(Form):
    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_query(self):
        return self.cleaned_data["query"]

    query = forms.CharField(required=True, )


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
        # self.fields["is_public"].label = "Public"

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

    # def clean_is_public(self):
    #    return self.cleaned_data["is_public"]

    class Meta:
        model = Paper
        fields = ["title", "abstract", "keywords", "download_link"]


class PaperUpdateForm(PaperForm):
    def __init__(self, *args, **kwargs):
        super(PaperForm, self).__init__(*args, **kwargs)

        self.fields["abstract"].widget = forms.Textarea()
        self.fields["abstract"].widget.attrs.update({"rows": "8"})
        self.fields["title"].label = "Title*"
        self.fields["abstract"].label = "Abstract*"
        self.fields["keywords"].label = "Keywords"
        self.fields["download_link"].label = "Download Link*"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

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
        label=mark_safe("Source URL*"),
        max_length=2000,
        widget=forms.TextInput(attrs={"size": 60}),
    )


class ProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["about"].label = "About"
        self.fields["affiliation"].label = "Affiliation"
        self.fields["interests"].label = "Interests"
        self.fields["job"].label = "Job title"
        self.fields["city"].label = "City"
        self.fields["country"].label = "Country"
        self.fields["website"].label = "Website (requires http:// or https://)"
        self.fields["github"].label = "Github (requires http:// or https://)"
        self.fields["linkedin"].label = "LinkedIn (requires http:// or https://)"
        self.fields["twitter"].label = "Twitter (requires http:// or https://)"

        self.fields["about"].widget = forms.Textarea()
        self.fields["about"].widget.attrs.update({"rows": "5"})
        self.fields["interests"].widget = forms.Textarea()
        self.fields["interests"].widget.attrs.update({"rows": "1"})
        self.fields["affiliation"].widget = forms.Textarea()
        self.fields["affiliation"].widget.attrs.update({"rows": "1"})

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            # visible.field.widget.attrs.update({"style": "width:25em"})
            # print(visible.field.widget.attrs.items())

    def clean_about(self):
        return self.cleaned_data["about"]

    def clean_affiliation(self):
        return self.cleaned_data["affiliation"]

    def clean_interests(self):
        return self.cleaned_data["interests"]

    def clean_job(self):
        return self.cleaned_data["job"]

    def clean_city(self):
        return self.cleaned_data["city"]

    def clean_country(self):
        return self.cleaned_data["country"]

    def clean_website(self):
        return self.cleaned_data["website"]

    def clean_github(self):
        return self.cleaned_data["github"]

    def clean_linkedin(self):
        return self.cleaned_data["linkedin"]

    def clean_twitter(self):
        return self.cleaned_data["twitter"]

    class Meta:
        model = Profile
        fields = ["about", "affiliation", "interests", "job", "city", "country", "website", "github", "linkedin",
                  "twitter"]


class PersonForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["name"].label = "Name"
        self.fields["name"].widget.attrs.update({"rows": "1"})

        self.fields["affiliation"].label = "Affiliation"
        self.fields["website"].label = "Website"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_affiliation(self):
        return self.cleaned_data["affiliation"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Person
        fields = ["name", "affiliation", "website"]


class DatasetForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        # The default for the description field widget is text input. Buy we want to display
        # more than one rows so we replace it with a Textarea widget.
        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})

        self.fields["name"].label = "Name"
        self.fields["keywords"].label = "Keywords"
        self.fields["description"].label = "Description"
        self.fields["dataset_type"].label = "Type"
        self.fields["publication_year"].label = "Publication Year"
        self.fields["publication_month"].label = "Publication Month"
        self.fields["website"].label = "Website (http:// or https://)"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_dataset_type(self):
        return self.cleaned_data["dataset_type"]

    def clean_publication_year(self):
        return self.cleaned_data["publication_year"]

    def clean_publication_month(self):
        return self.cleaned_data["publication_month"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Dataset
        fields = [
            "name",
            "keywords",
            "description",
            "dataset_type",
            "publication_year",
            "publication_month",
            "website",
        ]


class VenueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        self.fields["name"].label = "Name"
        self.fields["publisher"].label = "Publisher"
        self.fields["publication_year"].label = "Publication Year (yyyy)"
        self.fields["publication_month"].label = "Publication Month (mm)"
        self.fields["venue_type"].label = "Type"
        self.fields["peer_reviewed"].label = "Peer Reviewed"
        self.fields["keywords"].label = "Keywords"
        self.fields["website"].label = "Website (http:// or https://)"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_publisher(self):
        return self.cleaned_data["publisher"]

    def clean_publication_year(self):
        return self.cleaned_data["publication_year"]

    def clean_publication_month(self):
        return self.cleaned_data["publication_month"]

    def clean_venue_type(self):
        return self.cleaned_data["venue_type"]

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
            "publication_year",
            "publication_month",
            "venue_type",
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

    def clean_text(self):
        return self.cleaned_data["text"]

    def clean_publication_date(self):
        return self.cleaned_data["publication_date"]

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
        self.fields["name"].label = "Name"
        self.fields["website"].label = "Website (http:// or https://)"
        self.fields["keywords"].label = "Keywords"
        self.fields["description"].label = "Description"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_website(self):
        return self.cleaned_data["website"]

    class Meta:
        model = Code
        fields = ["name", "website", "keywords", "description"]


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

        self.fields["address"].widget = forms.Textarea()
        self.fields["address"].widget.attrs.update({"rows": "3"})

        self.fields["address"].label = "Building/Street/Suburb/Postcode"
        self.fields["city"].label = "City"
        self.fields["country"].label = "Country*"
        self.fields["room"].widget = forms.Textarea()
        self.fields["room"].widget.attrs.update({"rows": "1"})

        self.fields["day"].label = "Day"
        self.fields["start_time"].label = "Start Time (HH/MM/SS)"
        self.fields["end_time"].label = "Finish Time (HH/MM/SS)"
        self.fields["timezone"].label = "Timezone"
        self.fields["keywords"].label = "Keywords"
        self.fields["slack"].label = "Slack (requires https://)"
        self.fields["telegram"].label = "Telegram (requires https://)"
        self.fields["videoconferencing"].label = "WebEx, Skype, etc."
        self.fields["room"].lable = "Room"
        self.fields["description"].label = "Description"
        self.fields["name"].label = "Name"
        self.fields["is_public"].label = "Public"

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def clean(self):
        """Overriding in order to validate the start and finish times."""
        cleaned_data = super().clean()
        stime = cleaned_data.get("start_time")
        etime = cleaned_data.get("end_time")

        if etime < stime:
            raise forms.ValidationError("Finish time must be later than start time.")

        return cleaned_data

    def clean_address(self):
        return self.cleaned_data["address"]

    def clean_timezone(self):
        return self.cleaned_data["timezone"]

    def clean_country(self):
        return self.cleaned_data["country"]

    def clean_city(self):
        return self.cleaned_data["city"]

    def clean_day(self):
        return self.cleaned_data["day"]

    def clean_start_time(self):
        return self.cleaned_data["start_time"]

    def clean_end_time(self):
        return self.cleaned_data["end_time"]

    def clean_videoconferencing(self):
        return self.cleaned_data["videoconferencing"]

    def clean_room(self):
        return self.cleaned_data["room"]

    def clean_keywords(self):
        return self.cleaned_data["keywords"]

    def clean_description(self):
        return self.cleaned_data["description"]

    def clean_name(self):
        return self.cleaned_data["name"]

    def clean_slack(self):
        return self.cleaned_data["slack"]

    def clean_telegram(self):
        return self.cleaned_data["telegram"]

    class Meta:
        model = ReadingGroup
        fields = ["name", "description", "keywords", "address", "city", "country", "room",
                  "day", "timezone", "start_time", "end_time", "is_public", "slack", "telegram", "videoconferencing"]


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

        violation_types = (
            ("spam", "spam"),
            ("offensive", "offensive"),
            ("pornography", "pornography"),
            ("extremist", "extremist"),
            ("violence", "violence"),
        )

        self.fields["description"].widget = forms.Textarea()
        self.fields["description"].widget.attrs.update({"rows": "5"})
        self.fields["violation"] = forms.ChoiceField(choices=violation_types, widget=forms.RadioSelect())

        self.fields["description"].label = "Description"
        self.fields["violation"].label = "Violation"

    def clean_violation(self):
        return self.cleaned_data["violation"]

    def clean_description(self):
        return self.cleaned_data["description"]

    class Meta:
        model = CommentFlag
        fields = ['violation', 'description']


class PaperReportForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

        options = (
            ("title", "Title"),
            ("abstract", "Abstract"),
            ("authors", "Authors"),
            ("download", "Download link"),
            ("venue", "Venue"),
        )

        self.fields["error_type"] = forms.ChoiceField(choices=options, widget=forms.RadioSelect())
        self.fields["description_fb"].widget = forms.Textarea()
        self.fields["description_fb"].widget.attrs.update({"rows": "5"})

        self.fields["description_fb"].label = "Description"
        self.fields["error_type"].label = "Where"

    def clean_error_field(self):
        return self.cleaned_data["error_type"]

    def clean_description(self):
        return self.cleaned_data["description_fb"]

    class Meta:
        model = PaperReport
        fields = ['error_type', 'description_fb']