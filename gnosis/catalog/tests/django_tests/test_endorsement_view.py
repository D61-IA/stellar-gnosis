from django.test import TestCase
from catalog.models import Paper, Endorsement
from django.urls import reverse
from django.contrib.auth.models import User
import json


class EndorsementViewTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user1 = User.objects.create_user(username="testuser1", password="12345")
        self.user2 = User.objects.create_user(username='testuser2', password='54321')

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user1,
        )


    def test_log_in_redirect(self):
        """ Only a logged in user can endorse a paper or delete the endorsement"""

        # Expects a redirect to the login page if user is not logged in
        target_url = f"/accounts/login/?next=/catalog/endorsements/create/{self.paper.id}"
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))
        self.assertRedirects(response, expected_url=target_url, status_code=302, target_status_code=200)


    def test_endorsement_create(self):
        """Only a logged in user can create an endorsement for a paper """

        # Login the test user user1
        login = self.client.login(username='testuser1', password='12345')

        # Try creating a endorsement for that paper again
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['result'], "add")
        # Check we do not have 2 endorsement entries for the same paper
        endorsements = Endorsement.objects.filter(user=self.user1, paper=self.paper)
        self.assertEqual(len(endorsements), 1)

        self.client.logout()

        # Log in as test user user2
        login = self.client.login(username='testuser2', password='54321')

        # Check user2 does not have a endorsement
        endorsements = Endorsement.objects.filter(user=self.user2, paper=self.paper)
        self.assertEqual(len(endorsements), 0)

        self.client.logout()


    def test_endorsement_delete(self):
        """Only a logged in user can delete their endorsement for a paper """

        # Login user2
        login = self.client.login(username='testuser2', password='54321')
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        # Check user2 has a endorsement entry for the same paper
        endorsements = Endorsement.objects.filter(user=self.user2, paper=self.paper)
        self.assertEqual(len(endorsements), 1)
        self.client.logout()

        # Login user1
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        # Check user1 has a endorsement entry for the same paper
        endorsements = Endorsement.objects.filter(user=self.user1, paper=self.paper)
        self.assertEqual(len(endorsements), 1)
        # Delete endorsement for user1
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))
        self.assertEqual(json.loads(response.content)['result'], "delete")

        self.client.logout()

        # Check user1's endorsement is gone
        endorsements = Endorsement.objects.filter(user=self.user1, paper=self.paper)
        self.assertEqual(len(endorsements), 0)

        # Check user2 still has the endorsement
        endorsements = Endorsement.objects.filter(user=self.user2, paper=self.paper)
        self.assertEqual(len(endorsements), 1)

