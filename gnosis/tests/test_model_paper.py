from django.test import TestCase

from catalog.models import Paper
from neomodel.exceptions import RequiredProperty


# Create your tests here.
class PaperModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        pass

    def test_object_create(self):

        paper = Paper()
        paper.title = "No title"
        paper.abstract = "The abstract is missing."
        paper.keywords = ""
        paper.download_link = "https://google.com"

        self.assertEquals(paper.title, "No title")
        self.assertEquals(paper.__str__(), "No title")
        self.assertEquals(paper.abstract, "The abstract is missing.")
        self.assertEquals(paper.download_link, "https://google.com")
        self.assertEquals(len(paper.keywords), 0)

        paper = Paper()
        paper.abstract = "The abstract is missing."
        paper.keywords = ""
        paper.download_link = "https://google.com"

        try:  # It is missing required property title
            paper.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        paper = Paper()
        paper.title = "No title"
        paper.keywords = ""
        paper.download_link = "https://google.com"

        try:  # It is missing required property abstract
            paper.save()
        except RequiredProperty:
            assert True
        else:
            assert False

        paper = Paper()
        paper.title = "No title"
        paper.abstract = ""
        paper.keywords = ""

        try:  # It is missing required property download_link
            paper.save()
        except RequiredProperty:
            assert True
        else:
            assert False

    def test_create_duplicate(self):
        """
        Testing if the same paper can be added twice.
        For this test, a neo4j database must be running
        """
        paper = Paper(
            title="No title",
            abstract="The abstract is missing.",
            keywords="test, paper",
            download_link="https://google.com",
        )

        self.assertTrue(paper)

        # This will create an entry in the db.
        paper.save()

        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 1)

        # This will not create an entry in the db.
        paper.save()

        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 1)

        paper = Paper(
            title="No title",
            abstract="The abstract is missing.",
            keywords="test, paper",
            download_link="https://google.com",
        )

        self.assertTrue(paper)

        # This will not create an entry in the db.
        paper.save()

        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 2)

        for paper in papers:
            paper.delete()

        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 0)

    def test_create_delete_in_db(self):
        """ For this test, a neo4j database must be running """
        paper = Paper(
            title="No title",
            abstract="The abstract is missing.",
            keywords="test, paper",
            download_link="https://google.com",
        )

        self.assertTrue(paper)

        # This will create an entry in the db.
        paper.save()

        # Check if the paper was added to the DB by querying for it based on the title
        # and then checking if a paper is found.
        papers = Paper.nodes.filter(title="No title")

        self.assertEquals(len(papers), 1)

        # delete the paper from the DB
        papers[0].delete()

        # check if the paper was indeed deleted
        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 0)

    def test_create_delete_edge_db(self):
        """ For this test, a neo4j database must be running """
        paper_a = Paper(
            title="Paper A",
            abstract="The abstract is missing.",
            keywords="test, paper, A",
            download_link="https://google.com",
        )

        self.assertTrue(paper_a)

        paper_b = Paper(
            title="Paper B",
            abstract="The abstract is missing.",
            keywords="test, paper, B",
            download_link="https://google.com",
        )

        # This will create two entries in the db.
        paper_a.save()
        paper_b.save()

        # There should be no edge between these two papers in the db.
        # Check that this is true.

        self.assertEquals(len(paper_a.cites), 0)
        self.assertEquals(len(paper_b.cites), 0)

        # Add edge paper_a -> cites -> paper_b
        paper_a.cites.connect(paper_b)

        # This is a directed edge from paper_a to paper_b. Test this.
        self.assertEquals(len(paper_a.cites), 1)
        self.assertEquals(len(paper_b.cites), 0)

        # Delete the paper from the DB
        # This should also delete the edge between the two papers
        paper_a.delete()
        paper_b.delete()

        # check if the paper was indeed deleted
        papers = Paper.nodes.filter(title="No ")
        self.assertEquals(len(papers), 0)
