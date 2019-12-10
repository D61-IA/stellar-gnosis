from django.test import TestCase
from catalog.models import Code, Paper
from django.contrib.auth.models import User


class CodeTestCase(TestCase):
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

        # Create a Code repo entry
        self.code = Code.objects.create(
            name="StellarGraph",
            description="Python library for graph machine learning.",
            website="https://stellargraph.io",
            keywords="graph machine learning",
            created_by=self.user,
        )

    def test_code_creation(self):

        # There is only one Code in the DB
        self.assertEqual(Code.objects.all().count(), 1)
        self.assertEqual(self.code.name, "StellarGraph")
        self.assertEqual(self.code.description, "Python library for graph machine learning.")
        self.assertEqual(self.code.website, "https://stellargraph.io")
        self.assertEqual(self.code.keywords, "graph machine learning")
        self.assertEqual(self.code.created_by, self.user)

        # Try to create the same Code again
        code_b = Code.objects.create(
            name="StellarGraph",
            description="Python library for graph machine learning.",
            website="https://stellargraph.io",
            keywords="graph machine learning",
            created_by=self.user,
        )

        # There is nothing to prevent the creation of a Code with the same data
        self.assertEqual(Code.objects.all().count(), 2)

    def test_code_paper_relationship(self):

        # # Initially, the paper and Code are not linked
        self.assertEqual(self.code.papers.all().count(), 0)
        #
        # # Link the paper with the Code
        self.code.papers.add(self.paper)
        self.code.save()

        #
        self.assertEqual(self.code.papers.all().count(), 1)

        #
        # Create a second paper and link it with the Code object
        paper_b = Paper.objects.create(
             title="Second best paper in the world",
             abstract="The nature of gravity debunked.",
             download_link="https://google.com",
             created_by=self.user,
        )

        self.code.papers.add(paper_b)
        self.code.save()

        self.assertEqual(self.code.papers.all().count(), 2)
