import json

from django.test import TestCase
from catalog.models import Paper, PaperReport
from django.urls import reverse
from django.contrib.auth.models import User


class PaperModerationTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username="testuser", password="12345")

        self.admin = User.objects.create_superuser(
            username="admin", password="abcdefg", email="admin@gnosis.stellargraph.io"
        )

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )

        self.paper_report = PaperReport.objects.create(
            error_type='title',
            description_fb='Title error description',
            is_resolved=False,
            proposed_by=self.user,
            paper=self.paper,
        )

        print("this is called!")

    def test_login_redirect(self):
        """ Only an admin user can access the moderation page """
        response = self.client.get(reverse("reported_papers_index"))

        # You have to be logged in to access the moderation page
        # We should be redirected to the admin login page
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("reported_papers_index"))
        target_url = f"/admin/login/?next=/catalog/moderation/papers/reports/"

        # You have to be logged in to access the moderation page.
        # We should be redirected to the admin login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

        # Check an admin can access the moderation
        login = self.client.login(username="admin", password="abcdefg")
        response = self.client.get(reverse("reported_papers_index"))

        self.assertEqual(response.status_code, 200)


    def test_report_create(self):
        """Only a logged in user can report a paper"""
        # Login the test user user1
        login = self.client.login(username='testuser', password='12345')

        # Try report that paper again
        response = self.client.post(reverse("paper_error_report", kwargs={'id': self.paper.id}), {'error_type': 'title'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['is_valid'], True)

    def test_report_delete(self):
        """Only an admin can delete a report"""

        login = self.client.login(username='admin', password='abcdefg')
        response = self.client.post(reverse('paper_report_del', kwargs={'id': self.paper_report.id}))
        self.assertEqual(json.loads(response.content)['is_valid'], True)

        self.client.logout()

        paper_report = PaperReport.objects.filter(id=self.paper_report.id)
        self.assertEqual(len(paper_report), 0)

    def test_report_resolve(self):
        """Only an admin can resolve a report"""

        login = self.client.login(username='admin', password='abcdefg')
        response = self.client.post(reverse('paper_report_resl', kwargs={'id': self.paper_report.id}))
        self.assertEqual(json.loads(response.content)['is_resolved'], True)

        paper_report = PaperReport.objects.get(id=self.paper_report.id)
        # Check the report has been resolved
        is_resolved = paper_report.is_resolved
        self.assertEqual(is_resolved, True)

        self.client.logout()

    def test_report_unresolve(self):
        """Only an admin can unresolve a report"""

        login = self.client.login(username='admin', password='abcdefg')

        # Send POST to resolve twice to unresolve
        response = self.client.post(reverse('paper_report_resl', kwargs={'id': self.paper_report.id}))
        response = self.client.post(reverse('paper_report_resl', kwargs={'id': self.paper_report.id}))
        self.assertEqual(json.loads(response.content)['is_resolved'], False)

        paper_report = PaperReport.objects.get(id=self.paper_report.id)
        # Check the report has been unresolved
        is_resolved = paper_report.is_resolved
        self.assertEqual(is_resolved, False)

        self.client.logout()