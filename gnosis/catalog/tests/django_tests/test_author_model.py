from django.test import TestCase
from catalog.models import Person
from django.contrib.auth.models import User


class PersonTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        Person.objects.create(first_name='Pantelis', last_name='Elinas', created_by=None)
        Person.objects.create(first_name='Fiona', middle_name='Anne', last_name='Elliott', created_by=self.user)

    def test_person_creation(self):

        person_a = Person.objects.get(first_name='Pantelis')
        person_b = Person.objects.get(first_name='Fiona')

        self.assertEqual(person_a.first_name, 'Pantelis')
        self.assertEqual(person_a.last_name, 'Elinas')
        self.assertEqual(person_a.middle_name, None)
        self.assertEqual(person_a.created_by, None)

        self.assertEqual(person_b.first_name, 'Fiona')
        self.assertEqual(person_b.middle_name, 'Anne')
        self.assertEqual(person_b.last_name, 'Elliott')
        self.assertEqual(person_b.created_by, self.user)
