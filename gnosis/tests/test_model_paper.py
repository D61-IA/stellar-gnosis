from django.test import TestCase

from catalog.models import Paper, Person, Dataset, Venue, Code
from neomodel.exceptions import RequiredProperty
from neomodel import db

import datetime


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_model_people
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
        paper.id = "01"

        self.assertEquals(paper.title, "No title")
        self.assertEquals(paper.__str__(), "No title")
        self.assertEquals(paper.abstract, "The abstract is missing.")
        self.assertEquals(paper.download_link, "https://google.com")
        self.assertEquals(len(paper.keywords), 0)
        url = paper.get_absolute_url()

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

    # !!!!!!!!! THIS TEST WILL REMOVE PREVIOUS DUMMY DATA AND ANYTHING ASSOCIATED WITH DUMMY PAPER 'MAIN' !!!!!!!
    # def test_create_dummy_data(self):
    #     """
    #     create dummy papers for testing purposes
    #     """
    #     query = "MATCH (s:Paper {title: 'main'}) -- (p) DETACH DELETE p, s"
    #     # query = "MATCH (n) DETACH DELETE n"
    #     results, meta = db.cypher_query(query)
    #
    #     main_paper = Paper()
    #     main_paper.title = "main"
    #     main_paper.abstract = "This main paper has fewer connections"
    #     main_paper.download_link = "www.main.com"
    #     main_paper.save()
    #
    #     for i in range(20):
    #         venue = Venue()
    #         venue.name = "Venue " + str(i)
    #         venue.publisher = "Publisher"
    #         venue.publication_date = datetime.date.today()
    #         venue.type = "O"
    #         venue.peer_reviewed = "Y"
    #         venue.keywords = "Test venues"
    #         venue.save()
    #         main_paper.was_published_at.connect(venue)
    #
    #     for i in range(50):
    #         paper = Paper()
    #         title = "Paper " + str(i)
    #         abstract = "Abstract " + str(i)
    #         download_link = "www.DownloadLink" + str(i) + ".com"
    #         paper.title = title
    #         paper.abstract = abstract
    #         paper.keywords = "k"
    #         paper.download_link = download_link
    #         paper.save()
    #         paper.cites.connect(main_paper)
    #
    #     for i in range(30):
    #         code = Code()
    #         code.website = "www.DownloadLink" + str(i) + ".com"
    #         code.keywords = "Test code"
    #         code.description = "This is test code"
    #         code.save()
    #         code.implements.connect(main_paper)
    #
    #     for i in range(30):
    #         dataset = Dataset()
    #         dataset.name = "Dataset " + str(i)
    #         dataset.description = "Description " + str(i)
    #         dataset.keywords = "k"
    #         dataset.source_type = "N"
    #         dataset.save()
    #         main_paper.published.connect(dataset)
    #
    #     for i in range(30):
    #         person = Person()
    #         person.first_name = "FirstName"
    #         person.last_name = "Author " + str(i)
    #         person.middle_name = "FirstName " + "Author " + str(i)
    #         person.save()
    #         person.authors.connect(main_paper)

    def test_create_duplicate(self):
        """
        Testing if the same paper can be added twice.
        For this test, a neo4j database must be running
        """
        papers = Paper.nodes.filter(title="No title")

        # delete the paper from the DB
        for paper in papers:
            paper.delete()

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

        # This will create an entry in the db.
        paper.save()

        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 2)

        for paper in papers:
            print(paper)
            paper.delete()

        papers = Paper.nodes.filter(title="No title")
        self.assertEquals(len(papers), 0)

    def test_create_delete_in_db(self):
        """ For this test, a neo4j database must be running """
        papers = Paper.nodes.filter(title="No title")

        # delete the paper from the DB
        for paper in papers:
            paper.delete()

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
        for paper in papers:
            print(paper)
            paper.delete()

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
