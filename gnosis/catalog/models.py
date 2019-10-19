from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django_neomodel import DjangoNode
from django.urls import reverse
from neomodel import StringProperty, DateTimeProperty, DateProperty, UniqueIdProperty, \
    IntegerProperty, RelationshipTo


# Create your models here.
# This is the Neo4j model
# class Paper(DjangoNode):
#
#     uid = UniqueIdProperty()
#
#     created = DateTimeProperty(default=datetime.now())
#     created_by = IntegerProperty()  # The uid of the user who created this node
#
#     # These are always required
#     title = StringProperty(required=True)
#     abstract = StringProperty(required=True)
#     keywords = StringProperty(required=False)
#     download_link = StringProperty(required=True)
#     # added source link for a paper to record the source website which the information of paper is collected
#     source_link = StringProperty(required=False)
#
#
#     # Links
#     cites = RelationshipTo("Paper", "cites")
#     uses = RelationshipTo("Paper", "uses")
#     extends = RelationshipTo("Paper", "extends")
#     evaluates_on = RelationshipTo("Dataset", "evaluates_on")
#     was_published_at = RelationshipTo("Venue", "was_published_at")
#     published = RelationshipTo("Dataset", "published")
#
#     class Meta:
#         app_label = 'catalog'
#         ordering = ["title", "-published"]  # title is A-Z and published is from newest to oldest
#
#     def __str__(self):
#         """
#         String for representing the Paper object, e.g., in Admin site.
#         :return: The paper's title
#         """
#         return self.title
#
#     def get_absolute_url(self):
#         return reverse('paper_detail', args=[self.id])


# class Person(DjangoNode):
#
#     uid = UniqueIdProperty()
#     created = DateTimeProperty(default=datetime.now())
#     created_by = IntegerProperty()  # The uid of the user who created this node
#
#     # These are always required
#     first_name = StringProperty(required=True)
#     last_name = StringProperty(required=True)
#     middle_name = StringProperty()
#     affiliation = StringProperty()
#     website = StringProperty()
#
#     authors = RelationshipTo("Paper", "authors")
#     co_authors_with = RelationshipTo("Person", "co_authors_with")
#     advisor_of = RelationshipTo("Person", "advisor_of")
#
#     class Meta:
#         app_label = 'catalog'
#         ordering = ['last_name', 'first_name', 'affiliation']
#
#     def __str__(self):
#
#         if self.middle_name is not None and len(self.middle_name) > 0:
#             return '{} {} {}'.format(self.first_name, self.middle_name, self.last_name)
#         return '{} {}'.format(self.first_name, self.last_name)
#
#     def get_absolute_url(self):
#         return reverse('person_detail', args=[self.id])


class Dataset(DjangoNode):

    uid = UniqueIdProperty()
    created = DateTimeProperty(default=datetime.now())
    created_by = IntegerProperty()  # The uid of the user who created this node

    # These are always required
    name = StringProperty(required=True)
    # keywords that describe the dataset
    keywords = StringProperty(required=True)
    # A brief description of the dataset
    description = StringProperty(required=True)
    # The date of publication.
    publication_date = DateProperty(required=False)

    # data_types = {'N': 'Network', 'I': 'Image(s)', 'V': 'Video(s)', 'M': 'Mix'}
    data_types = (('N', 'Network'),
                  ('I', 'Image(s)'),
                  ('V', 'Video(s)'),
                  ('M', 'Mix'),)
    source_type = StringProperty(choices=data_types)
    website = StringProperty()

    # We should be able to link a dataset to a paper if the dataset was
    # published as part of the evaluation for a new algorithm. We note
    # that the Paper model already includes a link of type 'published'
    # so a dataset list or detail view should provide a link to add a
    # 'published' edge between a dataset and a paper.

    class Meta:
        app_label = 'catalog'
        ordering = ['name', 'type']

    def __str__(self):
        return '{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('dataset_detail', args=[self.id])


class Venue(DjangoNode):

    venue_types = (('J', 'Journal'),
                   ('C', 'Conference'),
                   ('W', 'Workshop'),
                   ('O', 'Open Source'),
                   ('R', 'Tech Report'),
                   ('O', 'Other'),)

    review_types = (('Y', 'Yes'),
                    ('N', 'No'),)

    uid = UniqueIdProperty()
    created = DateTimeProperty(default=datetime.now())
    created_by = IntegerProperty()  # The uid of the user who created this node

    # These are always required
    name = StringProperty(required=True)
    publication_date = DateProperty(required=True)
    type = StringProperty(required=True, choices=venue_types)  # journal, tech report, open source, conference, workshop
    publisher = StringProperty(required=True)
    keywords = StringProperty(required=True)

    peer_reviewed = StringProperty(required=True, choices=review_types)  # Yes or no
    website = StringProperty()

    class Meta:
        app_label = 'catalog'
        ordering = ['name', 'publisher', 'publication_date', 'type']

    def __str__(self):
        return '{} by {} on {}'.format(self.name, self.publisher, self.publication_date)

    def get_absolute_url(self):
        return reverse('venue_detail', args=[self.id])


#
# These are models for the SQL database
#

class Paper(models.Model):

    # uid = UniqueIdProperty()

    # These are always required
    title = models.CharField(max_length=500, blank=False)  # StringProperty(required=True)
    abstract = models.TextField(blank=False)  # StringProperty(required=True)
    keywords = models.CharField(max_length=125, blank=True)  #StringProperty(required=False)
    download_link = models.CharField(max_length=250, blank=False)  #StringProperty(required=True)
    # added source link for a paper to record the source website which the information of paper is collected
    source_link = models.CharField(max_length=250, blank=True)  # StringProperty(required=False)

    # created = DateTimeProperty(default=datetime.now())
    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,   # CASCADE, # what happens if I delete a user or a paper?
                                   related_name="papers_added",
                                   null=True)

    # Relationships/Edges
    # A Paper has a ManyToMany relationship with Person. We can access all the people associated with a paper,
    # using paper.person_set.all()
    # I can associate a paper with a person using
    # paper.person_set.add(person)

    # Links
    # cites = RelationshipTo("Paper", "cites")
    # uses = RelationshipTo("Paper", "uses")
    # extends = RelationshipTo("Paper", "extends")
    # evaluates_on = RelationshipTo("Dataset", "evaluates_on")
    # was_published_at = RelationshipTo("Venue", "was_published_at")
    # published = RelationshipTo("Dataset", "published")

    class Meta:
        app_label = 'catalog'
        ordering = ["title", "-created_at"]  # title is A-Z and published is from newest to oldest

    def __str__(self):
        """
        String for representing the Paper object, e.g., in Admin site.
        :return: The paper's title
        """
        return self.title

    def get_absolute_url(self):
        return reverse('paper_detail', args=[self.id])


class Code(models.Model):

    description = models.TextField(blank=False)
    website = models.CharField(max_length=225, blank=False)
    keywords = models.CharField(max_length=250, blank=False)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,  #CASCADE,
                                   related_name="codes_added", null=True)

    # A piece of Code can implement the algorithms in one or more papers.
    # We can add a paper to a Code object calling
    # code.papers.add(paper)
    # I can retrieve all papers implemented in some Code using
    # code.papers.all()
    papers = models.ManyToManyField(Paper)

    class Meta:
        app_label = 'catalog'
        ordering = ['website', 'description', 'keywords']

    def __str__(self):
        return '{}'.format(self.website)

    def get_absolute_url(self):
        return reverse('code_detail', args=[self.id])


class Comment(models.Model):

    text = models.TextField(blank=False)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.CASCADE,  # deleting a user deletes all her comments.
                                   related_name="author")

    # a paper can have many comments from several users.
    # The below creates a one-to-many relationship between the Paper and Comment models
    paper = models.ForeignKey(Paper,
                              on_delete=models.CASCADE,  # deleting a paper deletes all associated comments
                              )

    class Meta:
        app_label = 'catalog'
        ordering = ['created_at']

    def __str__(self):
        return '{}'.format(self.text)

    def get_absolute_url(self):
        return reverse('comment_detail', args=[self.id])


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
    # parson.papers.all()
    papers = models.ManyToManyField(Paper)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,  # CASCADE,
                                   related_name="person",
                                   null=True)

    class Meta:
        app_label = 'catalog'
        ordering = ['last_name', 'first_name', 'affiliation']

    def __str__(self):
        # print("--- middle name ---")
        # print(self.middle_name)
        if self.middle_name is not None and len(self.middle_name) > 0:
            return '{} {} {}'.format(self.first_name, self.middle_name, self.last_name)
        return '{} {}'.format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('person_detail', args=[self.id])


class ReadingGroup(models.Model):
    """A ReadingGroup model"""

    # Fields
    name = models.CharField(max_length=100,
                            help_text="Enter a name for your group.",
                            blank=False)
    description = models.TextField(help_text="Enter a description.",
                                   blank=False)
    keywords = models.CharField(max_length=100,
                                help_text="Keywords describing the group.",
                                blank=False)
    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    owner = models.ForeignKey(to=User,
                              on_delete=models.SET_NULL,  # CASCADE,
                              related_name="reading_groups",
                              null=True)

    # Metadata
    class Meta:
        ordering = ['name', '-created_at']

    # Methods
    def get_absolute_url(self):
        return reverse('group_detail', args=[str(self.id)])

    def __str__(self):
        return self.name


class ReadingGroupEntry(models.Model):
    """An entry, that is paper, in a reading group"""

    # Fields
    reading_group = models.ForeignKey(to=ReadingGroup,
                                      on_delete=models.CASCADE,
                                      related_name="papers")  # ReadingGroup.papers()

    paper_id = models.IntegerField(null=False, blank=False)  # A paper in the Neo4j DB
    paper_title = models.TextField(null=False, blank=False)  # The paper title to avoid extra DB calls
    proposed_by = models.ForeignKey(to=User,
                                    on_delete=models.SET_NULL,
                                    related_name="papers",
                                    null=True)  # User.papers()
    date_discussed = models.DateField(null=True, blank=True)
    date_proposed = models.DateField(auto_now_add=True, auto_now=False)

    def get_absolute_url(self):
        return reverse('group_detail', args=[str[self.id]])

    def __str__(self):
        return str(self.paper_id)


# Collections are private folders for user to organise their papers
class Collection(models.Model):
    """A Collection model"""

    # Fields
    name = models.CharField(max_length=100,
                            blank=False)
    description = models.TextField(null=True,
                                   blank=True)
    keywords = models.CharField(max_length=100,
                                null=True, blank=True)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)

    # deleting a user deletes all her collections
    owner = models.ForeignKey(to=User,
                              on_delete=models.CASCADE,
                              related_name="collections")

    # Metadata
    class Meta:
        ordering = ['name', '-created_at']

    # Methods
    def get_absolute_url(self):
        return reverse('collection_detail', args=[str(self.id)])

    def __str__(self):
        return self.name


class CollectionEntry(models.Model):
    """An entry, that is paper, in a reading group"""

    # Fields
    collection = models.ForeignKey(to=Collection,
                                   on_delete=models.CASCADE,
                                   related_name="papers")  # Collection.papers()

    # A paper in the Neo4j DB
    paper_id = models.IntegerField(null=False, blank=False)
    # The paper title to avoid extra DB calls
    paper_title = models.TextField(null=False, blank=False)

    created_at = models.DateField(auto_now_add=True, auto_now=False)

    def get_absolute_url(self):
        return reverse('collection_detail', args=[str[self.id]])

    def __str__(self):
        return str(self.paper_id)
