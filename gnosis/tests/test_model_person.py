from django.test import TestCase

from catalog.models import Person
from neomodel.exceptions import RequiredProperty


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_model_person
class PersonModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        pass

    def test_object_create(self):
        """ For this test, a neo4j database must be running """

        # test the creation of a person instance
        person = Person()
        person.first_name = "first"
        person.last_name = "last"
        person.affiliation = ""
        person.website = ""
        person.id = "01"

        url = person.get_absolute_url()

        self.assertEquals(person.__str__(),"first last")
        self.assertFalse(person.affiliation)
        self.assertFalse(person.website)

        person.middle_name = "middle"
        self.assertEquals(person.__str__(),"first middle last")

        # test first_name is required
        person.first_name = None
        try:  # It is missing required property first_name
            person.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test last_name is required
        person.first_name = "first"
        person.last_name = None
        try:  # It is missing required property last_name
            person.save()
        except RequiredProperty:
            assert True
        else:
            assert False

    def test_create_duplicate(self):
        """
        Testing if the same person can be added twice.
        For this test, a neo4j database must be running
        """
        person = Person(first_name="first", last_name="last")

        # This will create an entry in the db.
        person.save()

        people = Person.nodes.filter(first_name="first")
        self.assertEquals(len(people), 1)

        # This will not create an entry in the db.
        person.save()

        people = Person.nodes.filter(first_name="first")
        self.assertEquals(len(people), 1)

        person = Person(first_name="first", last_name="last")

        # This will create an entry in the db.
        person.save()

        people = Person.nodes.filter(first_name="first")
        self.assertEquals(len(people), 2)

        for person in people:
            person.delete()

        people = Person.nodes.filter(first_name="first")
        self.assertEquals(len(people), 0)

    def test_create_delete_in_db(self):
        """ For this test, a neo4j database must be running """
        person = Person(first_name="first", last_name="last")
        self.assertTrue(person)

        # This will create an entry in the db.
        person.save()

        # Check if the person was added to the DB by querying for it based on the first_name
        people = Person.nodes.filter(first_name="first")

        # A person should be found
        self.assertEquals(len(people), 1)

        # Delete the person from db
        people[0].delete()

        # test the person is removed
        people = Person.nodes.filter(first_name="first")
        self.assertTrue(len(people) == 0)

    def test_create_delete_edge_db(self):
        """ For this test, a neo4j database must be running """
        p1 = Person(first_name="first", last_name="last")

        p2 = Person(first_name="first", last_name="last")

        # This will create two entries in the db.
        p1.save()
        p2.save()

        # There should be no edge between these two person in the db.
        # Check that this is true.

        self.assertEquals(len(p1.co_authors_with), 0)
        self.assertEquals(len(p2.co_authors_with), 0)

        # Add edge p1 -> co_authors_with -> p2
        p1.co_authors_with.connect(p2)

        # This is a directed edge from p1 to p2. Test this.
        self.assertEquals(len(p1.co_authors_with), 1)
        self.assertEquals(len(p2.co_authors_with), 0)

        # Delete the person from the DB
        # This should also delete the edge between the two people
        p1.delete()
        p2.delete()

        # check if the people was indeed deleted
        people = Person.nodes.filter(first_name="first")
        self.assertEquals(len(people), 0)

