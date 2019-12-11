from django.test import TestCase
from catalog.models import Paper
from bookmark.models import Bookmark
from django.urls import reverse
from django.contrib.auth.models import User
import json


class BookmarkViewTestCase(TestCase):
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
        """ Only a logged in user can bookmark a paper"""
        # Expects a redirect to the login page if user is not logged in
        target_url = f"/accounts/login/?next=/catalog/paper/{self.paper.id}/bookmark"
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))
        self.assertRedirects(response, expected_url=target_url, status_code=302, target_status_code=200)


    def test_bookmark_create(self):

        # Login the test user user1
        login = self.client.login(username='testuser1', password='12345')

        # Try creating a bookmark for that paper again
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(json.loads(response.content)['result'], "add")

        # check we do not have 2 bookmark entries for the same paper
        bookmarks = Bookmark.objects.filter(owner=self.user1, paper=self.paper)
        self.assertEqual(len(bookmarks), 1)

        self.client.logout()

        # Log in as test user user2
        login = self.client.login(username='testuser2', password='54321')

        # check user2 does not have a bookmark
        bookmarks = Bookmark.objects.filter(owner=self.user2, paper=self.paper)
        self.assertEqual(len(bookmarks), 0)

        self.client.logout()


    def test_bookmark_delete(self):
        """ Only a logged in user can delete their own bookmarks"""

        # Login user2
        login = self.client.login(username='testuser2', password='54321')
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        # check user2 has a bookmark entry for the same paper
        bookmarks = Bookmark.objects.filter(owner=self.user2, paper=self.paper)
        self.assertEqual(len(bookmarks), 1)
        self.client.logout()

        # Login user1
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))
        self.assertEqual(response.status_code, 200)

        # check user1 has a bookmark entry for the same paper
        bookmarks = Bookmark.objects.filter(owner=self.user1, paper=self.paper)
        self.assertEqual(len(bookmarks), 1)

        # delete bookmark for user1
        response = self.client.post(reverse("paper_bookmark", kwargs={'id': self.paper.id}))
        self.assertEqual(json.loads(response.content)['result'], "add")

        self.client.logout()

        # check user1's bookmark is gone
        bookmarks = Bookmark.objects.filter(owner=self.user1, paper=self.paper)
        self.assertEqual(len(bookmarks), 0)

        # check user2 still has the same paper
        bookmarks = Bookmark.objects.filter(owner=self.user2, paper=self.paper)
        self.assertEqual(len(bookmarks), 1)

