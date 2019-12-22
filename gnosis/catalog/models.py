import calendar
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from timezone_field import TimeZoneField
from django.db.models.signals import post_save
from django.dispatch import receiver

#
def valid_code_website(value):
    """Basic website validation for Code entries. Only links to github.com are allowed for now."""
    if (not value.startswith("https://github.com")) and (
        not value.startswith("http://github.com")
    ):
        raise ValidationError(
            _("Invalid website %(value)s. Only links to github.com are allowed."),
            params={"value": value},
        )

###########################################
#                                         #
# These are models for the SQL database   #
#                                         #
###########################################
class Venue(models.Model):

    venue_types = (
        ("Journal", "Journal"),
        ("Conference", "Conference"),
        ("Workshop", "Workshop"),
        ("Open Source", "Open Source"),
        ("Tech Report", "Tech Report"),
        ("Other", "Other"),
    )
    review_types = (("Yes", "Yes"), ("No", "No"))

    venue_months = [
        (calendar.month_name[month], calendar.month_name[month])
        for month in range(1, 13)
    ]

    # These are always required
    name = models.CharField(max_length=250, blank=False)
    # publication_date = models.DateField()

    publication_year = models.SmallIntegerField(
        blank=False, validators=[MaxValueValidator(2020), MinValueValidator(1900)]
    )
    publication_month = models.CharField(
        max_length=25, blank=False, choices=venue_months
    )

    venue_type = models.CharField(max_length=50, choices=venue_types, blank=False)
    publisher = models.CharField(max_length=250, blank=True)
    keywords = models.CharField(max_length=250, blank=False)

    peer_reviewed = models.CharField(max_length=15, choices=review_types, blank=False)
    website = models.CharField(
        max_length=2000, blank=False, validators=[URLValidator()]
    )

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, related_name="venue", null=True
    )

    # Relationships
    # A Venue publishes zero or more papers so there is a one to many relationship between venue and paper
    # since a paper can only be published in a single venue.

    class Meta:
        app_label = "catalog"
        ordering = ["name", "publication_year", "publication_month", "venue_type"]

    def __str__(self):
        return "{} by {}, {}".format(self.name, self.publisher, self.publication_year)

    def get_absolute_url(self):
        return reverse("venue_detail", args=[self.id])

class Profile(models.Model):
    '''User profile as described at,
    https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    about = models.TextField(blank=True)
    affiliation = models.TextField(max_length=150, blank=True)
    interests = models.TextField(max_length=300, blank=True)
    job = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Paper(models.Model):

    # These are always required
    title = models.CharField(max_length=500, blank=False)
    abstract = models.TextField(blank=False)
    keywords = models.CharField(max_length=125, blank=True)
    # download_link = models.CharField(max_length=250, blank=False)
    download_link = models.CharField(
        max_length=2000, blank=False, null=False, validators=[URLValidator()]
    )

    is_public = models.BooleanField(default=True, null=False, blank=False)
    # added source link for a paper to record the source website which the information of paper is collected
    source_link = models.CharField(max_length=250, blank=True)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, related_name="papers_added", null=True
    )

    was_published_at = models.ForeignKey(
        to=Venue, on_delete=models.SET_NULL, blank=True, null=True
    )

    # relationships with other papers using a "through" model to denote the
    # type of relationship, one of cites, extends, uses. A paper can have 0 or more
    # relationships with other papers.
    # The relationship is not symmetric.
    papers = models.ManyToManyField(
        "self",
        through="PaperRelationshipType",
        through_fields=("paper_from", "paper_to"),
        symmetrical=False,
        blank=True,
    )

    # Relationships/Edges
    # A Paper has a ManyToMany relationship with Person. We can access all the people associated with a paper,
    # using paper.person_set.all()
    # I can associate a paper with a person using
    # paper.person_set.add(person)

    class Meta:
        app_label = "catalog"
        ordering = [
            "title",
            "-created_at",
        ]  # title is A-Z and published is from newest to oldest

    def __str__(self):
        """
        String for representing the Paper object, e.g., in Admin site.
        :return: The paper's title
        """
        return self.title

    def get_absolute_url(self):
        return reverse("paper_detail", args=[self.id])


class PaperRelationshipType(models.Model):

    edge_types = (("cites", "cites"), ("uses", "uses"), ("extends", "extends"))

    # The type of relationship
    relationship_type = models.CharField(
        max_length=25, choices=edge_types, blank=False, null=False
    )

    created_at = models.DateField(default=datetime.date.today)
    updated_at = models.DateField(null=True)

    paper_from = models.ForeignKey(
        Paper, related_name="paper_from", on_delete=models.CASCADE
    )

    paper_to = models.ForeignKey(
        Paper, related_name="paper_to", on_delete=models.CASCADE
    )


class Code(models.Model):

    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False)
    website = models.CharField(
        max_length=2000, blank=False, validators=[URLValidator(), valid_code_website]
    )
    keywords = models.CharField(max_length=250, blank=False)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,  # CASCADE,
        related_name="codes_added",
        null=True,
    )

    # A piece of Code can implement the algorithms in one or more papers.
    # We can add a paper to a Code object calling
    # code.papers.add(paper)
    # I can retrieve all papers implemented in some Code using
    # code.papers.all()
    papers = models.ManyToManyField(Paper)

    class Meta:
        app_label = "catalog"
        ordering = ["name", "website", "description", "keywords"]

    def __str__(self):
        return "{}".format(self.name)

    def get_absolute_url(self):
        return reverse("code_detail", args=[self.id])


class Comment(models.Model):

    text = models.TextField(blank=False)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,  # deleting a user deletes all her comments.
        related_name="author",
    )

    is_flagged = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    # a paper can have many comments from several users.
    # The below creates a one-to-many relationship between the Paper and Comment models
    paper = models.ForeignKey(
        Paper,
        on_delete=models.CASCADE,  # deleting a paper deletes all associated comments
    )


    class Meta:
        app_label = "catalog"
        ordering = ["created_at"]

    def __str__(self):
        return "{}".format(self.text)

    def get_absolute_url(self):
        return reverse("comment_detail", args=[self.id])


class Person(models.Model):

    # These are always required
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    affiliation = models.CharField(max_length=250, blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)

    # A Paper can have many authors and an author can have many papers.
    # We can add a paper to an author/person by calling
    # person.papers.add(paper)
    # I can retrieve all papers by a person using
    # person.papers.all()
    papers = models.ManyToManyField(
        Paper, through="PaperAuthorRelationshipData", symmetrical=False, blank=True
    )

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, related_name="person", null=True  # CASCADE,
    )

    class Meta:
        app_label = "catalog"
        ordering = ["last_name", "first_name", "affiliation"]

    def __str__(self):
        # print("--- middle name ---")
        # print(self.middle_name)
        if self.middle_name is not None and len(self.middle_name) > 0:
            return "{} {} {}".format(self.first_name, self.middle_name, self.last_name)
        return "{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse("person_detail", args=[self.id])


class PaperAuthorRelationshipData(models.Model):
    # The author order, 1st, 2nd, 3rd, etc.
    order = models.SmallIntegerField(
        null=False,
        blank=False,
        default=1,
        validators=[
            MaxValueValidator(40),  # allows up to 40 authors
            MinValueValidator(1),
        ],  # minimum is at least a first author
    )

    paper = models.ForeignKey(
        Paper, related_name="source_paper", on_delete=models.CASCADE
    )

    author = models.ForeignKey(Person, related_name="author", on_delete=models.CASCADE)


class Dataset(models.Model):

    months = [
        (calendar.month_name[month], calendar.month_name[month])
        for month in range(1, 13)
    ]

    # These are always required
    name = models.CharField(max_length=300, blank=False)
    # keywords that describe the dataset
    keywords = models.CharField(max_length=300, blank=False)
    # A brief description of the dataset
    description = models.TextField(blank=False, null=False)
    # The date of publication.
    publication_year = models.SmallIntegerField(
        blank=False, validators=[MaxValueValidator(2020), MinValueValidator(1900)]
    )
    publication_month = models.CharField(max_length=25, blank=True, choices=months)

    data_types = (
        ("Network", "Network"),
        ("Image(s)", "Image(s)"),
        ("Video(s)", "Video(s)"),
        ("Audio", "Audio"),
        ("Biology", "Biology"),
        ("Chemistry", "Chemistry"),
        ("Astronomy", "Astronomy"),
        ("Physics", "Physics"),
        ("Other", "Other"),
    )

    dataset_type = models.CharField(max_length=50, choices=data_types, blank=False)
    website = models.CharField(
        max_length=2000, blank=False, validators=[URLValidator()]
    )

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True  # CASCADE,
    )

    # A Paper can evaluate on zero or more datasets.
    # We can add a paper to a dataset by calling
    # dataset.papers.add(paper)
    # I can retrieve all papers evaluating on a dataset using
    # dataset.papers.all()
    #papers = models.ManyToManyField(Paper)

    papers = models.ManyToManyField(
        Paper, through="PaperDatasetRelationshipData", symmetrical=False, blank=True
    )


    class Meta:
        app_label = "catalog"
        ordering = ["name", "publication_year", "dataset_type"]

    def __str__(self):
        return "{}".format(self.name)

    def get_absolute_url(self):
        return reverse("dataset_detail", args=[self.id])

class PaperDatasetRelationshipData(models.Model):
    # Future proofing for when we want to store evaluation data published in a paper
    # on a given dataset.
    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)

    from_paper = models.ForeignKey(
        Paper, related_name="from_paper", on_delete=models.CASCADE
    )

    dataset = models.ForeignKey(Dataset, related_name="dataset", on_delete=models.CASCADE)


class CommentFlag(models.Model):

    violation_types = (
        ("spam", "spam"),
        ("offensive", "offensive"),
        ("pornography", "pornography"),
        ("extremist", "extremist"),
        ("violence", "violence"),
    )

    comment = models.ForeignKey(
        to=Comment, null=False, blank=False, on_delete=models.CASCADE
    )
    violation = models.CharField(
        max_length=50, choices=violation_types, null=False, blank=False
    )
    # The user has to give a more detailed description.
    description = models.TextField(null=False, blank=False)

    # user who flagged the comment
    proposed_by = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="comment_flags"
    )

    created_at = models.DateField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ["violation", "-created_at"]
        verbose_name = "comment flag"

    # Methods
    def get_absolute_url(self):
        return reverse("comment_flag_detail", args=[str(self.id)])

    def __str__(self):
        return self.description


# A ReadingGroup member for private groups
class ReadingGroupMember(models.Model):

    permissions = (
        ("granted", "granted"),
        ("requested", "requested"),
        ("banned", "banned"),
        ("none", "none"),
    )

    # the user who is the member
    member = models.ForeignKey(to=User, on_delete=models.CASCADE, null=False)
    access_type = models.CharField(max_length=50, choices=permissions, blank=False)
    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)

    def __str__(self):
        return str(self.member)


class ReadingGroup(models.Model):
    """A ReadingGroup model"""

    days = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday")
    )

    city_validator = RegexValidator(r'^[a-zA-Z\s]*$', 'Only alphabetic characters are allowed.')

    # Fields
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    keywords = models.CharField(max_length=100, blank=False)
    is_public = models.BooleanField(default=False, blank=False, null=False)
    videoconferencing = models.TextField(blank=True, null=True, default='')
    room = models.TextField(max_length=150, blank=True, null=True, default='')

    day = models.CharField(max_length=9, choices=days, blank=False, default="Monday")
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)

    timezone = TimeZoneField(default='Australia/Sydney',
                             display_GMT_offset=True,
                             null=False,
                             blank=False)

    address = models.CharField(max_length=255, default='', blank=True)

    city = models.CharField(max_length=75,
                            default="Sydney",
                            blank=False,
                            null=False,
                            validators=[city_validator])

    country = CountryField(default='AU', blank=False, null=False)

    slack = models.URLField(blank=True, null=True)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    owner = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,  # CASCADE,
        related_name="reading_groups",
        null=True,
    )
    # For private groups, this is the list of users who have requested to join, having been granted access, or
    # banned from the group.
    members = models.ManyToManyField(ReadingGroupMember)

    # Metadata
    class Meta:
        ordering = ["name", "-created_at"]

    # Methods
    def get_absolute_url(self):
        return reverse("group_detail", args=[str(self.id)])

    def __str__(self):
        return self.name


class ReadingGroupEntry(models.Model):
    """An entry, that is paper, in a reading group"""

    # Fields
    reading_group = models.ForeignKey(
        to=ReadingGroup, on_delete=models.CASCADE, related_name="papers"
    )  # ReadingGroup.papers()

    paper = models.ForeignKey(
        to=Paper,
        on_delete=models.CASCADE,
        related_name="groups",
        null=False,
        blank=False,
    )  # Paper.groups()

    proposed_by = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, related_name="papers", null=True
    )  # User.papers()

    date_discussed = models.DateField(null=True, blank=True)
    date_proposed = models.DateField(auto_now_add=True, auto_now=False)

    def get_absolute_url(self):
        return reverse("group_detail", args=[str(self.id)])

    def __str__(self):
        return str(self.paper.id)


# Collections are private folders for user to organise their papers
class Collection(models.Model):
    """A Collection model"""

    # Fields
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)

    # deleting a user deletes all her collections
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="collections"
    )

    # Metadata
    class Meta:
        ordering = ["name", "-created_at"]

    # Methods
    def get_absolute_url(self):
        return reverse("collection_detail", args=[str(self.id)])

    def __str__(self):
        return self.name


class CollectionEntry(models.Model):
    """An entry, that is paper, in a reading group"""

    # Fields
    collection = models.ForeignKey(
        to=Collection, on_delete=models.CASCADE, related_name="papers"
    )  # Collection.papers()

    paper = models.ForeignKey(
        to=Paper, on_delete=models.CASCADE, related_name="collections"
    )  # Paper.collections()

    # paper_id = models.IntegerField(null=False, blank=False)
    # The paper title to avoid extra DB calls
    # paper_title = models.TextField(null=False, blank=False)
    created_at = models.DateField(auto_now_add=True, auto_now=False)

    def get_absolute_url(self):
        return reverse("collection_detail", args=[str(self.id)])

    def __str__(self):
        return str(self.paper)


class Endorsement(models.Model):
    """An entry, that is user, in an endorsement for a paper"""

    # Fields
    paper = models.ForeignKey(
        to=Paper, on_delete=models.CASCADE, related_name="endorsements"
    )  # Paper.endorsements()

    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="endorsements"
    )  # User.endorsements()

    created_at = models.DateField(auto_now_add=True, auto_now=False)

    # Metadata
    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("endorsements")

    def __str__(self):
        return str(self.user) + " endorse " + str(self.paper.title)
