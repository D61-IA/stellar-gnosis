from django.test import TestCase
from catalog.models import Code, Paper
from django.urls import reverse
from django.contrib.auth.models import User


class CodeViewsTestCase(TestCase):
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

        self.code_stellargraph = Code.objects.create(
            name="StellarGraph",
            description="Python library for graph machine learning.",
            website="https://stellargraph.io",
            keywords="graph machine learning",
            created_by=self.user,
        )

        self.code_tensorflow = Code.objects.create(
            name="TensorFlow",
            description="Python library for machine learning.",
            website="https://tensorflow.org",
            keywords="machine learning",
            created_by=self.user,
        )

    def test_codes_view(self):
        """ Any user should be able to access the index view """
        response = self.client.get(reverse("codes_index"))

        # One venue we created in setUp()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['codes'].count(), 2)

    def test_code_delete(self):
        """ Only an admin user can delete a Code entry """
        response = self.client.get(reverse("code_delete", kwargs={'id': self.code_stellargraph.id}))

        # You have to be logged in to access the delete view
        # We should be redirected to the admin login page
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("code_delete", kwargs={'id': self.code_stellargraph.id}))
        target_url = f"/admin/login/?next=/catalog/code/{self.code_stellargraph.id}/delete/"

        # You have to be logged in to access the delete view.
        # However, only an admin can delete and object so we should be redirected to the admin login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

        # Create an admin/superuser and try again. Admins have access to the delete view
        login = self.client.login(username='admin', password='abcdefg')
        response = self.client.get(reverse("code_delete", kwargs={'id': self.code_stellargraph.id}))
        # Calling delete redirects to the people index page
        target_url = f"/catalog/codes/"
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

    def test_code_update(self):
        """ Only the logged in user can call update"""
        response = self.client.get(reverse("code_detail", kwargs={'id': self.code_stellargraph.id}))

        # Anyone can access the detail view
        self.assertEqual(response.status_code, 200)

        # User must be logged in to access the update view
        # The user should be redirected to login
        response = self.client.get(reverse("code_update", kwargs={'id': self.code_stellargraph.id}))
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("code_update", kwargs={'id': self.code_stellargraph.id}))
        # Any logged in user can access the update view.
        self.assertEqual(response.status_code, 200)

        # Logout
        self.client.logout()

    def test_code_create(self):
        """Only logged in users can create a new Code object"""
        target_url = "/accounts/login/?next=/catalog/code/create/"

        response = self.client.get(reverse("code_create"))

        # We should be redirected to the account login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("code_create"))
        # Any logged in user can access the create view.
        self.assertEqual(response.status_code, 200)

        self.client.logout()
