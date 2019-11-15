from django.test import TestCase
from catalog.models import Person, Venue, Paper
from django.urls import reverse
from django.contrib.auth.models import User


class VenueViewsTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username="testuser", password="12345")

        self.admin = User.objects.create_superuser(username='admin',
                                                   password='abcdefg',
                                                   email="admin@gnosis.stellargraph.io")

        # Create two people
        self.pantelis = Person.objects.create(
            first_name="Pantelis", last_name="Elinas", created_by=None
        )
        self.fiona = Person.objects.create(
            first_name="Fiona",
            middle_name="Anne",
            last_name="Elliott",
            created_by=self.user,
        )

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )

        self.venue = Venue.objects.create(
            name="ICCV",
            publication_year=2017,
            publication_month="July",
            venue_type="Conference",
            peer_reviewed="Yes",
            website="http://openaccess.thecvf.com/ICCV2017.py",
            created_by=self.user,
        )

    def test_venues_view(self):
        """ Any user should be able to access the index view """
        response = self.client.get(reverse("venues_index"))

        # One venue we created in setUp()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['venues'].count(), 1)

    def test_venue_delete(self):
        """ Only an admin user can delete an author """
        response = self.client.get(reverse("venue_delete", kwargs={'id': self.venue.id}))

        # You have to be logged in to access the delete view
        # We should be redirected to the admin login page
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("venue_delete", kwargs={'id': self.venue.id}))
        target_url = f"/admin/login/?next=/catalog/venue/{self.venue.id}/delete"

        # You have to be logged in to access the delete view.
        # However, only an admin can delete and object so we should be redirected to the admin login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

        # Create an admin/superuser and try again. Admins have access to the delete view
        login = self.client.login(username='admin', password='abcdefg')
        response = self.client.get(reverse("venue_delete", kwargs={'id': self.venue.id}))
        # Calling delete redirects to the people index page
        target_url = f"/catalog/venues/"
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()




    def test_venue_update(self):
        """ Only the logged in user can call update"""
        response = self.client.get(reverse("venue_detail", kwargs={'id': self.venue.id}))

        # Anyone can access the detail view
        self.assertEqual(response.status_code, 200)

        # User must be logged in to access the update view
        # The user should be redirected to login
        response = self.client.get(reverse("venue_update", kwargs={'id': self.venue.id}))
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("venue_update", kwargs={'id': self.venue.id}))
        # Any logged in user can access the update view.
        self.assertEqual(response.status_code, 200)

        # Logout
        self.client.logout()

    def test_venue_create(self):
        """Only logged in users can create a new person object"""
        target_url = "/accounts/login/?next=/catalog/venue/create/"

        response = self.client.get(reverse("venue_create"))

        # We should be redirected to the account login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("venue_create"))
        # Any logged in user can access the create view.
        self.assertEqual(response.status_code, 200)

        self.client.logout()
