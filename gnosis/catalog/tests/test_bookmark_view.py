from django.test import TestCase
from catalog.models import Paper
from bookmark.models import Bookmark
from django.urls import reverse
from django.contrib.auth.models import User


class BookmarkViewTestCase(TestCase):
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


    def test_bookmark_create(self):
        """ Only a logged in user can bookmark a paper"""
        response = self.client.post(reverse("paper_bookmark"), kwargs={'id': self.paper.id})

        # Expects a redirect to the login page if user is not logged in
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        # Try creating a bookmark for that paper again
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content, '{"bookmark": "add"}')

        self.client.logout()


    def test_bookmark_delete(self):
        """ Only a logged in user can bookmark a paper"""

        # create a bookmark for test paper
        bm = Bookmark.objects.create(paper=self.paper, owner=self.user)

        response = self.client.post(reverse("paper_bookmark"), kwargs={'id': self.paper.id})

        # Expects a redirect to the login page if user is not logged in
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        # Try creating a bookmark for that paper again
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.content, '{"bookmark": "delete"}')

        self.client.logout()




