from django.test import TestCase
from catalog.models import Profile
from django.urls import reverse
from django.contrib.auth.models import User


class ProfileViewsTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username="user1",
                                             password="12345",
                                             email="user1@gnosis.stellargraph.io")

        self.user2 = User.objects.create_user(username="user2",
                                              password="54321",
                                              email="user2@gnosis.stellargraph.io")

        self.admin = User.objects.create_superuser(username='admin',
                                                   password='abcdefg',
                                                   email="admin@gnosis.stellargraph.io")

    def test_profile_view(self):
        """Only logged in users can view user profiles"""

        # Viewing user profile details is only available to logged in user. The below
        # call should redirect to the login view
        response = self.client.get(reverse("profile", kwargs={'id': self.user.id}))

        # Only logged in user can view a user's profile; other get redirected to the login page
        target_url = f"/accounts/login/?next=/catalog/profile/{self.user.id}"

        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Login the test user
        login = self.client.login(username='user1', password='12345')

        response = self.client.get(reverse("profile", kwargs={'id': self.user.id}))

        # Can view her profile
        self.assertEqual(response.status_code, 200)
        # user1 should be able to edit their profile
        self.assertContains(response, f"catalog/profile/update")

        response = self.client.get(reverse("profile", kwargs={'id': self.user2.id}))

        # Can view another user's profile
        self.assertEqual(response.status_code, 200)

        # but cannot edit the other user's profile
        self.assertNotContains(response, f"catalog/profile/update")

        self.client.logout()

    def test_profile_update(self):
        """ Only the logged in user can call update"""

        # User must be logged in to access the update view
        # The user should be redirected to login
        response = self.client.get(reverse("profile_update"))
        target_url = f"/accounts/login/?next=/catalog/profile/update"

        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Login the test user
        login = self.client.login(username='user1', password='12345')

        response = self.client.get(reverse("profile_update"))
        # Any logged in user can access the update view.
        self.assertEqual(response.status_code, 200)

        # Let's check to make sure that this is user1's profile and not another user's
        self.assertContains(response, f"Update your profile {self.user}")

        # Logout
        self.client.logout()