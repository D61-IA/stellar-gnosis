from django.test import TestCase

from catalog.models import Paper, Person, Dataset, Venue
from neomodel.exceptions import RequiredProperty
import datetime as dt


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_relationship_across_models
class VenueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        pass

    def test_across_edges(self):
        """ For this test, a neo4j database must be running """
        paper = Paper(
            title="Paper",
            abstract="The abstract is missing.",
            keywords="test, paper",
            download_link="https://google.com",
        )
        self.assertTrue(paper)

        person = Person(first_name="first", last_name="last")
        self.assertTrue(person)

        dataset = Dataset(name="set",
                          keywords="ML",
                          description="machine learning papers",
                          source_type="N")
        self.assertTrue(dataset)

        venue = Venue(name="paper",
                      publication_date=dt.date(2019, 4, 17),
                      type="J",
                      publisher="CSIRO",
                      keywords="J",
                      peer_reviewed="N")
        self.assertTrue(venue)

        # Save all entries to the db.
        paper.save()
        person.save()
        dataset.save()
        venue.save()

        # There should be no edge across entries now in the db
        self.assertEquals(len(paper.evaluates_on), 0)
        self.assertEquals(len(paper.was_published_at), 0)
        self.assertEquals(len(paper.published), 0)
        self.assertEquals(len(person.authors), 0)

        # Add edge paper -> evaluates_on -> dataset
        paper.evaluates_on.connect(dataset)
        # Test it
        self.assertEquals(len(paper.evaluates_on), 1)

        # Test that duplicate edges cannot exist in the database
        paper.evaluates_on.connect(dataset)
        self.assertEquals(len(paper.evaluates_on), 1)

        # Add edge paper -> was_published_at -> venue
        paper.was_published_at.connect(venue)
        # Test it
        self.assertEquals(len(paper.was_published_at), 1)

        # Test that duplicate edges cannot exist in the database
        paper.was_published_at.connect(venue)
        self.assertEquals(len(paper.was_published_at), 1)

        # Add edge paper -> published -> dataset
        paper.published.connect(dataset)
        # Test it
        self.assertEquals(len(paper.published), 1)

        # Test that duplicate edges cannot exist in the database
        paper.published.connect(dataset)
        self.assertEquals(len(paper.published), 1)

        # Add edge person -> authors -> paper
        person.authors.connect(paper)
        # Test it
        self.assertEquals(len(person.authors), 1)

        # Test that duplicate edges cannot exist in the database
        person.authors.connect(paper)
        self.assertEquals(len(person.authors), 1)

        # Delete the entries from the DB
        # This should also delete all the edges
        paper.delete()
        person.delete()
        dataset.delete()
        venue.delete()

        # check if the entries were indeed deleted
        papers = Paper.nodes.filter(title="Paper")
        self.assertEquals(len(papers), 0)
        people = Person.nodes.filter(first_name="first")
        self.assertEquals(len(people), 0)
        datasets = Dataset.nodes.filter(name="set")
        self.assertEquals(len(datasets), 0)
        venues = Venue.nodes.filter(name="Paper")
        self.assertEquals(len(venues), 0)

