from django.test import TestCase
from catalog.models import Dataset, Paper
from django.urls import reverse
from django.contrib.auth.models import User


class DatasetViewsTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username="testuser", password="12345")

        self.admin = User.objects.create_superuser(username='admin',
                                                   password='abcdefg',
                                                   email="admin@gnosis.stellargraph.io")

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )

        self.dataset_cora = Dataset.objects.create(
            name="Cora",
            keywords="network, citation graph",
            description="A citation network dataset.",
            publication_year=2015,
            publication_month="October",
            dataset_type="Network",
            website="https://scholar.google.com",
            created_by=self.user,
        )

        self.dataset_pubmed = Dataset.objects.create(
            name="Pubmed",
            keywords="network, citation graph",
            description="A medical publications citation graph.",
            publication_year=2000,
            publication_month="December",
            dataset_type="Network",
            website="https://scholar.google.com",
            created_by=self.user,
        )

    def test_datasets_view(self):
        """ Any user should be able to access the index view """
        response = self.client.get(reverse("datasets_index"))

        # One venue we created in setUp()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['datasets'].count(), 2)

    def test_dataset_delete(self):
        """ Only an admin user can delete a dataset """
        response = self.client.get(reverse("dataset_delete", kwargs={'id': self.dataset_cora.id}))

        # You have to be logged in to access the delete view
        # We should be redirected to the admin login page
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("dataset_delete", kwargs={'id': self.dataset_cora.id}))
        target_url = f"/admin/login/?next=/catalog/dataset/{self.dataset_cora.id}/delete/"

        # You have to be logged in to access the delete view.
        # However, only an admin can delete and object so we should be redirected to the admin login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

        # Create an admin/superuser and try again. Admins have access to the delete view
        login = self.client.login(username='admin', password='abcdefg')
        response = self.client.get(reverse("dataset_delete", kwargs={'id': self.dataset_cora.id}))
        # Calling delete redirects to the people index page
        target_url = f"/catalog/datasets/"
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

    def test_dataset_update(self):
        """ Only the logged in user can call update"""
        response = self.client.get(reverse("dataset_detail", kwargs={'id': self.dataset_cora.id}))

        # Anyone can access the detail view
        self.assertEqual(response.status_code, 200)

        # User must be logged in to access the update view
        # The user should be redirected to login
        response = self.client.get(reverse("dataset_update", kwargs={'id': self.dataset_cora.id}))
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("dataset_update", kwargs={'id': self.dataset_cora.id}))
        # Any logged in user can access the update view.
        self.assertEqual(response.status_code, 200)

        # Logout
        self.client.logout()

    def test_dataset_create(self):
        """Only logged in users can create a new dataset object"""
        target_url = "/accounts/login/?next=/catalog/dataset/create/"

        response = self.client.get(reverse("dataset_create"))

        # We should be redirected to the account login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("dataset_create"))
        # Any logged in user can access the create view.
        self.assertEqual(response.status_code, 200)

        self.client.logout()
