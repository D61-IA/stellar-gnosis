import calendar
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator


###########################################
#                                         #
# These are models for the SQL database   #
#                                         #
###########################################
class Venue(models.Model):

    venue_types = (('Journal', 'Journal'),
                   ('Conference', 'Conference'),
                   ('Workshop', 'Workshop'),
                   ('Open Source', 'Open Source'),
                   ('Tech Report', 'Tech Report'),
                   ('Other', 'Other'),)
    review_types = (('Yes', 'Yes'),
                    ('No', 'No'),)

    venue_months = [(calendar.month_name[month], calendar.month_name[month]) for month in range(1, 13)]

    # These are always required
    name = models.CharField(max_length=250, blank=False)
    # publication_date = models.DateField()

    publication_year = models.SmallIntegerField(blank=False,
                                                validators=[MaxValueValidator(2020),
                                                            MinValueValidator(1900)])
    publication_month = models.CharField(max_length=25, blank=False, choices=venue_months)

    venue_type = models.CharField(max_length=50, choices=venue_types, blank=False)
    publisher = models.CharField(max_length=250, blank=True)
    keywords = models.CharField(max_length=250, blank=False)

    peer_reviewed = models.CharField(max_length=15, choices=review_types, blank=False)
    website = models.CharField(max_length=300, blank=True)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,
                                   related_name="venue",
                                   null=True)

    # Relationships
    # A Venue publishes zero or more papers so there is a one to many relationship between venue and paper
    # since a paper can only be published in a single venue.

    class Meta:
        app_label = 'catalog'
        ordering = ['name', 'publication_year', 'publication_month', 'venue_type']

    def __str__(self):
        return '{} by {}, {}'.format(self.name, self.publisher, self.publication_year)

    def get_absolute_url(self):
        return reverse('venue_detail', args=[self.id])


class Paper(models.Model):

    # These are always required
    title = models.CharField(max_length=500, blank=False)
    abstract = models.TextField(blank=False)
    keywords = models.CharField(max_length=125, blank=True)
    download_link = models.CharField(max_length=250, blank=False)
    # added source link for a paper to record the source website which the information of paper is collected
    source_link = models.CharField(max_length=250, blank=True)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,
                                   related_name="papers_added",
                                   null=True)

    was_published_at = models.ForeignKey(to=Venue,
                                         on_delete=models.SET_NULL,
                                         blank=True,
                                         null=True)

    # relationships with other papers using a "through" model to denote the
    # type of relationship, one of cites, extends, uses. A paper can have 0 or more
    # relationships with other papers.
    # The relationship is not symmetric.
    papers = models.ManyToManyField("self",
                                    through='PaperRelationshipType',
                                    through_fields=('paper_from', 'paper_to'),
                                    symmetrical=False,
                                    blank=True)

    # Relationships/Edges
    # A Paper has a ManyToMany relationship with Person. We can access all the people associated with a paper,
    # using paper.person_set.all()
    # I can associate a paper with a person using
    # paper.person_set.add(person)

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


class PaperRelationshipType(models.Model):

    edge_types = (('cites', 'cites'),
                  ('uses', 'uses'),
                  ('extends', 'extends'),
                  )

    # The type of relationship
    relationship_type = models.CharField(max_length=25,
                                         choices=edge_types,
                                         blank=False,
                                         null=False)

    created_at = models.DateField(default=datetime.date.today)
    updated_at = models.DateField(null=True)

    paper_from = models.ForeignKey(Paper,
                                   related_name="paper_from",
                                   on_delete=models.CASCADE)

    paper_to = models.ForeignKey(Paper,
                                 related_name="paper_to",
                                 on_delete=models.CASCADE)


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


class Dataset(models.Model):

    months = [(calendar.month_name[month], calendar.month_name[month]) for month in range(1, 13)]

    # These are always required
    name = models.CharField(max_length=300, blank=False)
    # keywords that describe the dataset
    keywords = models.CharField(max_length=300, blank=False)
    # A brief description of the dataset
    description = models.TextField(blank=False, null=False)
    # The date of publication.
    publication_year = models.SmallIntegerField(blank=False,
                                                validators=[MaxValueValidator(2020),
                                                            MinValueValidator(1900)])
    publication_month = models.CharField(max_length=25, blank=True, choices=months)

    data_types = (('Network', 'Network'),
                  ('Image(s)', 'Image(s)'),
                  ('Video(s)', 'Video(s)'),
                  ('Audio', 'Audio'),
                  ('Biology', 'Biology'),
                  ('Chemistry', 'Chemistry'),
                  ('Astronomy', 'Astronomy'),
                  ('Physics', 'Physics'),
                  ('Other', 'Other'), )

    dataset_type = models.CharField(max_length=50, choices=data_types, blank=False)
    website = models.CharField(max_length=300, blank=False)

    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(null=True)
    created_by = models.ForeignKey(to=User,
                                   on_delete=models.SET_NULL,  # CASCADE,
                                   null=True)

    # A Paper can evaluate on zero or more datasets.
    # We can add a paper to a dataset by calling
    # dataset.papers.add(paper)
    # I can retrieve all papers evaluating on a dataset using
    # dataset.papers.all()
    papers = models.ManyToManyField(Paper)

    class Meta:
        app_label = 'catalog'
        ordering = ['name', 'publication_year', 'dataset_type']

    def __str__(self):
        return '{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('dataset_detail', args=[self.id])

    #
    # These are models for the SQL database
    #


class CommentFlag(models.Model):
    comment_id = models.IntegerField(null=False, blank=False)  # id of the flagged comment

    violation = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateField(auto_now_add=True, auto_now=False)

    # user who flags the item
    proposed_by = models.ForeignKey(to=User,
                                    on_delete=models.CASCADE,
                                    related_name="comment_flags")

    class Meta:
        ordering = ['violation', '-created_at']
        verbose_name = "comment flag"

    # Methods
    def get_absolute_url(self):
        return reverse('paper_detail', args=[str(self.id)])

    def __str__(self):
        return self.description


# class HiddenComment(models.Model):
#     comment_id = models.IntegerField(null=False, blank=False)
#     proposed_by = models.ForeignKey(to=User,
#                                     on_delete=models.CASCADE,
#                                     related_name="hidden_flags")
#
#     class Meta:
#         ordering = ['proposed_by', 'comment_id']
#         verbose_name = "hidden flag"
#
#     def __str__(self):
#         return "comment id: " + str(self.comment_id)


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

    # paper_id = models.IntegerField(null=False, blank=False)  # A paper in the Neo4j DB
    # paper_title = models.TextField(null=False, blank=False)  # The paper title to avoid extra DB calls
    paper = models.ForeignKey(to=Paper,
                              on_delete=models.CASCADE,
                              related_name="groups",
                              null=False,
                              blank=False)  # Paper.groups()

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

    paper = models.ForeignKey(to=Paper,
                              on_delete=models.CASCADE,
                              related_name="collections")  # Paper.collections()

    # paper_id = models.IntegerField(null=False, blank=False)
    # The paper title to avoid extra DB calls
    # paper_title = models.TextField(null=False, blank=False)
    created_at = models.DateField(auto_now_add=True, auto_now=False)

    def get_absolute_url(self):
        return reverse('collection_detail', args=[str(self.id)])

    def __str__(self):
        return str(self.paper)


class EndorsementEntry(models.Model):
    """An entry, that is user, in an endorsement for a paper"""

    # Fields
    paper_id = models.IntegerField(null=False, blank=False)
    paper_title = models.TextField(null=False, blank=False)  # The paper title to avoid extra DB calls

    user = models.ForeignKey(to=User,
                             on_delete=models.CASCADE,
                             related_name="endorsements")

    created_at = models.DateField(auto_now_add=True, auto_now=False)

    # Metadata
    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('paper_detail', args=[str(self.id)])

    def __str__(self):
        return str(self.user) + ' endorse ' + str(self.paper_title)
