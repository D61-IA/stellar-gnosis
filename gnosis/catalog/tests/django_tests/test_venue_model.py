from django.test import TestCase
from catalog.models import Venue, Paper, Person
from django.contrib.auth.models import User


class VenueTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username="testuser", password="12345")

        # Create two people
        self.pantelis = Person.objects.create(
            name="Pantelis Elinas", created_by=None
        )
        self.fiona = Person.objects.create(
            name="Fiona Anne Elliott",
            created_by=self.user,
        )

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )

        self.venue_a = Venue.objects.create(
            name="ICCV",
            publication_year=2017,
            publication_month="July",
            venue_type="Conference",
            peer_reviewed="Yes",
            website="http://openaccess.thecvf.com/ICCV2017.py",
            created_by=self.user,
        )

    def test_venue_creation(self):

        venue_a = Venue.objects.get(name="ICCV")

        self.assertEqual(venue_a.name, "ICCV")
        self.assertEqual(venue_a.publication_year, 2017)
        self.assertEqual(venue_a.venue_type, "Conference")
        self.assertEqual(venue_a.keywords, "")
        self.assertEqual(venue_a.created_by, self.user)

        # Try to create the same venue again
        venue_b = Venue.objects.create(
            name="ICCV",
            publication_year=2017,
            publication_month="July",
            venue_type="Conference",
            peer_reviewed="Yes",
            website="http://openaccess.thecvf.com/ICCV2017.py",
            created_by=self.user,
        )
        # There is nothing to prevent the creation of a Venue with the same data
        self.assertEqual(Venue.objects.all().count(), 2)

        # Try to create another venue with all the same info but different year
        venue_b = Venue.objects.create(
            name="ICCV",
            publication_year=2015,
            publication_month="July",
            venue_type="Conference",
            peer_reviewed="Yes",
            website="http://openaccess.thecvf.com/ICCV2017.py",
            created_by=self.user,
        )

        self.assertEqual(Venue.objects.all().count(), 3)

    def test_venue_paper_relationship(self):

        # Initially, the paper and venue are not linked
        self.assertEqual(self.paper.was_published_at, None)

        # Link the paper with the venue
        self.paper.was_published_at = self.venue_a
        self.paper.save()

        self.assertEqual(self.paper.was_published_at, self.venue_a)

        # Retrieve all papers published at self.venue_a.
        papers = self.venue_a.paper_set.all()
        self.assertEqual(papers.count(), 1)

        # Create a second paper and link it with the venue
        # Create a paper
        paper_b = Paper.objects.create(
            title="Second best paper in the world",
            abstract="The nature of gravity debunked.",
            download_link="https://google.com",
            created_by=self.user,
        )

        paper_b.was_published_at = self.venue_a
        paper_b.save()

        # Retrieve all papers published at self.venue_a.
        papers = self.venue_a.paper_set.all()
        self.assertEqual(papers.count(), 2)
