from django.test import TestCase

from catalog.models import Dataset
from neomodel.exceptions import RequiredProperty
import datetime as dt


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_model_dataset
class DataSetModelTest(TestCase):

    def test_object_create(self):
        """ For this test, a neo4j database must be running """

        # test the creation of a dataset instance
        dataset = Dataset()
        dataset.id = "01"
        dataset.name = "set"
        dataset.keywords = "ML"
        dataset.description = "machine learning papers"
        dataset.source_type = "N"
        dataset.website = ""

        url = dataset.get_absolute_url()

        self.assertEquals(dataset.name, "set")
        self.assertEquals(dataset.keywords, "ML")
        self.assertEquals(dataset.description, "machine learning papers")
        self.assertEquals(dataset.source_type, "N")
        self.assertFalse(dataset.website)
        self.assertEquals(dataset.__str__(), "set")

        # test name is required
        dataset.name = None
        try:  # It is missing required property first_name
            dataset.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test keyword is required
        dataset.name = "set"
        dataset.keywords = None
        try:  # It is missing required property last_name
            dataset.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        # test description is required
        dataset.keywords = "ML"
        dataset.description = None
        try:  # It is missing required property last_name
            dataset.save()
        except RequiredProperty:
            assert True
        else:
            assert False

    def test_create_delete_in_db(self):
        """ For this test, a neo4j database must be running """

        dataset = Dataset(name="set",
                          keywords="ML",
                          description="machine learning papers",
                          source_type="N")

        self.assertTrue(dataset)

        # This will create an entry in the db.
        dataset.save()

        # Check if the dataset was added to the DB by querying for it based on the first_name
        datasets = Dataset.nodes.filter(name="set")

        # A person should be found
        self.assertEquals(len(datasets), 1)

        # Delete the person from db
        datasets[0].delete()

        # test the person is removed
        datasets = Dataset.nodes.filter(name="set")
        self.assertEquals(len(datasets), 0)

