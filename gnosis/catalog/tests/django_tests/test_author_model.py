from django.test import TestCase
from catalog.models import Person
from django.contrib.auth.models import User


class PersonTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        Person.objects.create(name='Pantelis Elinas', created_by=None)
        Person.objects.create(name='Fiona Anne Elliott', created_by=self.user)

    def test_person_creation(self):

        person_a = Person.objects.get(name='Pantelis Elinas')
        person_b = Person.objects.get(name='Fiona Anne Elliott')

        self.assertEqual(person_a.name, 'Pantelis Elinas')
        self.assertEqual(person_a.created_by, None)

        self.assertEqual(person_b.name, 'Fiona Anne Elliott')
        self.assertEqual(person_b.created_by, self.user)
