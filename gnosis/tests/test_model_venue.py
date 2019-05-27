from django.test import TestCase

from catalog.models import Venue
from neomodel.exceptions import RequiredProperty
import datetime as dt


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_model_venue
class VenueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        pass

    def test_object_create(self):
        """ For this test, a neo4j database must be running """

        # test the creation of a dataset instance
        venue = Venue()
        venue.name = "paper"
        time = dt.date(2019, 4, 17)
        venue.publication_date = time
        venue.type = "J"
        venue.publisher = "CSIRO"
        venue.keywords = "J"
        venue.peer_reviewed = "N"
        venue.id = "01"

        self.assertEquals(venue.publication_date, time)
        self.assertEquals(venue.type, "J")
        self.assertEquals(venue.keywords, "J")
        self.assertEquals(venue.peer_reviewed, "N")
        self.assertEquals(venue.__str__(), "paper by CSIRO on 2019-04-17")
        url = venue.get_absolute_url()

        # test name is required
        venue.name = None
        try:  # It is missing required property name
            venue.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test publication_date is required
        venue.name = "paper"
        venue.publication_date = None
        try:  # It is missing required property publication_date
            venue.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test type is required
        venue.publication_date = time
        venue.type = None
        try:  # It is missing required property type
            venue.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test publisher is required
        venue.type = "J"
        venue.publisher = None
        try:  # It is missing required property publisher
            venue.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test keywords is required
        venue.publisher = "CSIRO"
        venue.keywords = None
        try:  # It is missing required property keywords
            venue.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test peer_reviewed is required
        venue.keywords = "J"
        venue.peer_reviewed = None
        try:  # It is missing required property peer-reviewed
            venue.save()
        except RequiredProperty:
            assert True
        else:
            assert False

    def test_create_delete_in_db(self):
        """ For this test, a neo4j database must be running """

        venue = Venue(name="paper",
                      publication_date = dt.date(2019,4,17),
                      type = "J",
                      publisher = "CSIRO",
                      keywords = "J",
                      peer_reviewed = "N")

        self.assertTrue(venue)

        # This will create an entry in the db.
        venue.save()

        self.assertTrue(venue.type in [i for (i,_) in venue.venue_types])
        self.assertTrue(venue.__str__() == "paper by CSIRO on 2019-04-17")

        # Check if the dataset was added to the DB by querying for it based on the first_name
        venues = Venue.nodes.filter(name="paper")

        # A person should be found
        self.assertEquals(len(venues), 1)

        # Delete the person from db
        for v in venues:
            v.delete()

        # test the person is removed
        venues = Venue.nodes.filter(name="paper")
        self.assertEquals(len(venues), 0)

