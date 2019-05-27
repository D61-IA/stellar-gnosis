from datetime import datetime
from django_neomodel import DjangoNode
from django.urls import reverse
from neomodel import StringProperty, DateTimeProperty, DateProperty, UniqueIdProperty, \
    IntegerProperty, RelationshipTo


# Create your models here.
class Paper(DjangoNode):

    uid = UniqueIdProperty()

    created = DateTimeProperty(default=datetime.now())
    created_by = IntegerProperty()  # The uid of the user who created this node

    # These are always required
    title = StringProperty(required=True)
    abstract = StringProperty(required=True)
    keywords = StringProperty(required=False)
    download_link = StringProperty(required=True)
    # added source link for a paper to record the source website which the information of paper is collected
    source_link = StringProperty(required=False)


    # Links
    cites = RelationshipTo("Paper", "cites")
    uses = RelationshipTo("Paper", "uses")
    extends = RelationshipTo("Paper", "extends")
    evaluates_on = RelationshipTo("Dataset", "evaluates_on")
    was_published_at = RelationshipTo("Venue", "was_published_at")
    published = RelationshipTo("Dataset", "published")

    class Meta:
        app_label = 'catalog'
        ordering = ["title", "-published"]  # title is A-Z and published is from newest to oldest

    def __str__(self):
        """
        String for representing the Paper object, e.g., in Admin site.
        :return: The paper's title
        """
        return self.title

    def get_absolute_url(self):
        return reverse('paper_detail', args=[self.id])


class Person(DjangoNode):

    uid = UniqueIdProperty()
    created = DateTimeProperty(default=datetime.now())
    created_by = IntegerProperty()  # The uid of the user who created this node

    # These are always required
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    middle_name = StringProperty()
    affiliation = StringProperty()
    website = StringProperty()

    authors = RelationshipTo("Paper", "authors")
    co_authors_with = RelationshipTo("Person", "co_authors_with")
    advisor_of = RelationshipTo("Person", "advisor_of")

    class Meta:
        app_label = 'catalog'
        ordering = ['last_name', 'first_name', 'affiliation']

    def __str__(self):

        if self.middle_name is not None and len(self.middle_name) > 0:
            return '{} {} {}'.format(self.first_name, self.middle_name, self.last_name)
        return '{} {}'.format(self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('person_detail', args=[self.id])


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


class Comment(DjangoNode):

    uid = UniqueIdProperty()
    created = DateTimeProperty(default=datetime.now())
    created_by = IntegerProperty()  # The uid of the user who created this node

    # These are always required
    author = StringProperty()  # required but should be able to get it from user object
    text = StringProperty(required=True)

    publication_date = DateTimeProperty(default_now=True)

    discusses = RelationshipTo("Paper", "discusses")

    class Meta:
        app_label = 'catalog'
        ordering = ['publication_date']

    def __str__(self):
        return '{%s}'.format(self.author)

    def get_absolute_url(self):
        return reverse('comment_detail', args=[self.id])


class Code(DjangoNode):

    uid = UniqueIdProperty()
    created = DateTimeProperty(default=datetime.now())
    created_by = IntegerProperty()  # The uid of the user who created this node

    description = StringProperty(required=True)
    website = StringProperty(required=True)
    keywords = StringProperty(required=True)

    implements = RelationshipTo("Paper", "implements")

    class Meta:
        app_label = 'catalog'
        ordering = ['website', 'description', 'keywords']

    def __str__(self):
        return '{}'.format(self.website)

    def get_absolute_url(self):
        return reverse('code_detail', args=[self.id])
