from django.test import TestCase
from catalog.models import ReadingGroup, Paper
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime


class ReadingGroupViewsTestCase(TestCase):
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

        current_time = datetime.now()
        start_time = current_time.replace(hour=11, minute=0 )
        end_time = current_time.replace(hour=12, minute=30)

        # this is a public group
        self.ml_group_public = ReadingGroup.objects.create(name='ml public', description='Machine Learning journal club',
                                                    keywords='machine learning', is_public=True, videoconferencing='',
                                                    room='R101', day='Tuesday', start_time=start_time, end_time=end_time,
                                                    address='11 Keith street, Dulwich Hill', city='Sydney', country='AU',
                                                    owner=self.admin)
        # this is a private group
        self.ml_group_private = ReadingGroup.objects.create(name='ml private', description='Machine Learning journal club',
                                                    keywords='machine learning', is_public=False, videoconferencing='',
                                                    room='R101', day='Tuesday', start_time=start_time, end_time=end_time,
                                                    address='11 Keith street, Dulwich Hill', city='Sydney', country='AU',
                                                    owner=self.admin)


    def test_groups_view(self):
        """ Any user should be able to access the index view """
        response = self.client.get(reverse("groups_index"))

        # Two groups we created in setUp()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['groups'].count(), 2)

    def test_code_delete(self):
        """ Only a group owner can delete a ReadingGroup entry """
        response = self.client.get(reverse("group_delete", kwargs={'id': self.ml_group_private.id}))

        # You have to be logged in to access the delete view
        # We should be redirected to the login page
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("group_delete", kwargs={'id': self.ml_group_private.id}))
        # target_url = f"/admin/login/?next=/catalog/group/{self.ml_group_private.id}/delete"
        target_url = f"/catalog/groups"

        # You have to be logged in to access the delete view.
        # However, only the group owner can delete a group so we should be redirected to the groups index page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        self.client.logout()

        # Login as admin who is the owner of the group
        login = self.client.login(username='admin', password='abcdefg')
        response = self.client.get(reverse("group_delete", kwargs={'id': self.ml_group_private.id}))
        # Calling delete redirects to the groups index view after deleting the group
        target_url = f"/catalog/groups"
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        response = self.client.get(reverse("groups_index"))
        self.assertEqual(response.context['groups'].count(), 1)

        self.client.logout()

        # All users now only see 1 group
        response = self.client.get(reverse("groups_index"))
        self.assertEqual(response.context['groups'].count(), 1)


    def test_group_create(self):
        """Only logged in users can create a new ReadingGroup object"""
        target_url = "/accounts/login/?next=/catalog/group/create/"

        response = self.client.get(reverse("group_create"))

        # We should be redirected to the account login page
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("group_create"))
        # Any logged in user can access the create view.
        self.assertEqual(response.status_code, 200)

        self.client.logout()

    def test_group_update(self):
        """ Only the group owner if logged in can call update"""
        response = self.client.get(reverse("group_detail", kwargs={'id': self.ml_group_private.id}))

        # Anyone can access the detail view
        self.assertEqual(response.status_code, 200)

        # this is a private group, so the user, if not logged in and not a member, should not be able to 
        # see all details.

        # ToDo: Add some tests for this behavior here.

        # User must be logged in to access the update view
        # The user should be redirected to login
        response = self.client.get(reverse("group_update", kwargs={'id': self.ml_group_private.id}))
        self.assertEqual(response.status_code, 302)

        # Login the test user who is not the owner of this group. The test user should not have access to the udpate
        # view for this group.
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("group_update", kwargs={'id': self.ml_group_private.id}))
        # Only the group owner can access the update view.
        target_url = f"/catalog/group/{self.ml_group_private.id}"
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)

        # Same holds for public groups if the user is not the owner.
        response = self.client.get(reverse("group_update", kwargs={'id': self.ml_group_public.id}))
        # Only the group owner can access the update view.
        target_url = f"/catalog/group/{self.ml_group_public.id}"
        self.assertRedirects(response,
                             expected_url=target_url,
                             status_code=302,
                             target_status_code=200,)


        # Logout user test
        self.client.logout()

        # admin is the owner of both the public and private groups, so admin should have access to the update
        # views for each.
        login = self.client.login(username='admin', password='abcdefg')

        response = self.client.get(reverse("group_update", kwargs={'id': self.ml_group_private.id}))
        self.assertEqual(response.status_code, 200)

        # Same holds for public groups if the user is not the owner.
        response = self.client.get(reverse("group_update", kwargs={'id': self.ml_group_public.id}))
        # Only the group owner can access the update view.
        target_url = f"/catalog/group/{self.ml_group_public.id}"
        self.assertEqual(response.status_code, 200)

        # Logout user admin
        self.client.logout()


