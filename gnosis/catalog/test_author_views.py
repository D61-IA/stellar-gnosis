from django.test import TestCase
from catalog.models import Person
from django.urls import reverse
from django.contrib.auth.models import User


class PersonViewsTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username='testuser', password='12345')
        #login = self.client.login(username='testuser', password='12345')

        Person.objects.create(first_name='Pantelis', last_name='Elinas', created_by=None)
        Person.objects.create(first_name='Fiona', middle_name='Anne', last_name='Elliott', created_by=self.user)

    def test_persons_view(self):
        """ Any user should be able to access the index view """
        response = self.client.get(reverse("persons_index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['people'].count(), 2)

    def test_person_update(self):
        """ Only the logged in user can call update"""
        person = Person.objects.get(first_name='Fiona')
        response = self.client.get(reverse("person_detail", kwargs={'id': person.id}))

        # Anyone can access the detail view
        self.assertEqual(response.status_code, 200)

        # User must be logged in to access the update view
        # The user should be redirected to login
        response = self.client.get(reverse("person_update", kwargs={'id': person.id}))
        self.assertEqual(response.status_code, 302)

        # Login the test user
        login = self.client.login(username='testuser', password='12345')

        response = self.client.get(reverse("person_update", kwargs={'id': person.id}))
        self.assertEqual(response.status_code, 200)

    def test_person_delete(self):
        """ Only an admin user can delete an author """
        pass
