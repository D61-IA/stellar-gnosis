from django.test import TestCase
from catalog.models import Paper, Endorsement
from django.urls import reverse
from django.contrib.auth.models import User
import json

class EndorsementViewTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="12345")

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )


    def test_endorsement_create(self):
        """ Only a logged in user can endorse a paper"""
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))

        # Expects a redirect to the login page if user is not logged in
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        # Try creating a endorsement for that paper again
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(json.loads(response.content)['result'], "add")

        self.client.logout()


    def test_endorsement_delete(self):
        """ Only a logged in user can endorse a paper"""

        endorsement = Endorsement.objects.create(paper=self.paper, user=self.user)

        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))

        # Expects a redirect to the login page if user is not logged in
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        # Try creating a endorsement for that paper again
        response = self.client.post(reverse("endorsement_create", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(json.loads(response.content)['result'], "delete")

        self.client.logout()