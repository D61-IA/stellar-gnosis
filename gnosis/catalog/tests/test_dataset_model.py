from django.test import TestCase
from catalog.models import Dataset, Paper
from django.contrib.auth.models import User


class DatasetTestCase(TestCase):
    def setUp(self):
        #
        self.user = User.objects.create_user(username="testuser", password="12345")

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )

        self.dataset = Dataset.objects.create(
            name="Cora",
            keywords="network, citation graph",
            description="A citation network dataset.",
            publication_year=2015,
            publication_month="October",
            dataset_type="Network",
            website="https://scholar.google.com",
            created_by=self.user,
        )

    def test_dataset_creation(self):

        # There is only one dataset in the DB
        self.assertEqual(Dataset.objects.all().count(), 1)

        self.assertEqual(self.dataset.name, "Cora")
        self.assertEqual(self.dataset.publication_year, 2015)
        self.assertEqual(self.dataset.publication_month, "October")
        self.assertEqual(self.dataset.keywords, "network, citation graph")
        self.assertEqual(self.dataset.description, "A citation network dataset.")
        self.assertEqual(self.dataset.website, "https://scholar.google.com")
        self.assertEqual(self.dataset.dataset_type, "Network")
        self.assertEqual(self.dataset.created_by, self.user)

        # Try to create the same venue again
        dataset_b = Dataset.objects.create(
            name="Cora",
            keywords="network, citation graph",
            description="A citation network dataset.",
            publication_year=2015,
            publication_month="October",
            dataset_type="Network",
            website="https://scholar.google.com",
            created_by=self.user,
        )

        # There is nothing to prevent the creation of a Venue with the same data
        self.assertEqual(Dataset.objects.all().count(), 2)

    def test_dataset_paper_relationship(self):

        # # Initially, the paper and venue are not linked
        self.assertEqual(self.dataset.papers.all().count(), 0)
        #
        # # Link the paper with the venue
        self.dataset.papers.add(self.paper)
        self.dataset.save()

        #
        self.assertEqual(self.dataset.papers.all().count(), 1)

        #
        # Create a second paper and link it with the dataset
        paper_b = Paper.objects.create(
             title="Second best paper in the world",
             abstract="The nature of gravity debunked.",
             download_link="https://google.com",
             created_by=self.user,
        )

        self.dataset.papers.add(paper_b)
        self.dataset.save()

        self.assertEqual(self.dataset.papers.all().count(), 2)