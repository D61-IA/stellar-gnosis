from django.test import TestCase
from django.urls import reverse
from catalog.models import CommentFlag, Paper
from django.contrib.auth.models import User
from neomodel import db


# must connect to neo4j to run tests
class FlaggedCommentViewTest(TestCase):

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        CommentFlag.objects.create(
            comment_id=1,
            description="test description",
            violation="unwanted commercial content or spam",
            proposed_by=test_user1
        )

        paper = Paper()
        paper.title = "No title"
        paper.abstract = "The abstract is missing."
        paper.keywords = ""
        paper.download_link = "https://google.com"
        paper.save()

        self.paper_id = paper.id
        self.user_id = test_user1.id

    def tearDown(self):
        User.objects.filter(id=self.user_id).delete()
        query = "MATCH (a:Paper) WHERE ID(a)={id} DETACH DELETE a"
        results, meta = db.cypher_query(query, dict(id=self.paper_id))

    def test_fl_form_without_login(self):
        fl_form_data = {
            'violation': 'unwanted commercial content or spam',
            'description': 'test description'
        }

        # test POST request
        response = self.client.post(reverse('paper_detail', kwargs={'id': self.paper_id}), fl_form_data)
        self.assertEqual(response.status_code, 400)

    def test_fl_form_redirect(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        fl_form_data = {
            'violation': 'unwanted commercial content or spam',
            'description': 'test description',
            'comment_id': 1
        }

        # test POST request
        response = self.client.post(reverse('paper_detail', kwargs={'id': self.paper_id}), fl_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('paper_detail', kwargs={'id': self.paper_id}))
