from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.models import Paper
from catalog.views.views import paper_create, papers, \
    paper_connect_code, paper_connect_dataset, paper_connect_paper, paper_connect_author, \
    paper_connect_venue, paper_find, paper_detail, paper_remove_author, paper_authors

from django.http import HttpRequest


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_form_paper
class PaperViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')
        test_superuser1 = User.objects.create_superuser(username='superuser1', password='abc123', email='superuser123@gnosis.com')

        test_user1.save()
        test_user2.save()
        test_superuser1.save()

    # def test_paper_create(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = paper_create(request)
    #     self.assertEquals(response.status_code, 200)        # test if response is correct
    #     self.assertTrue("New Paper" in str(response.content) and "Title*" in str(response.content)
    #                     and "Abstract" in str(response.content) and "Keywords" in str(response.content))
    #
    # def test_papers(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.session = {}
    #     response = papers(request)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct
    #
    # def test_paper_connect_code(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     request.session = {}
    #     response = paper_connect_code(request)
    #     self.assertEquals(response.status_code, 200)
    #
    #
    # def test_paper_connect_dataset(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     request.session = {}
    #     response = paper_connect_dataset(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_paper_connect_paper(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     request.session = {}
    #     response = paper_connect_paper(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_paper_connect_author(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     request.session = {}
    #     response = paper_connect_author(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_paper_connect_venue(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     request.session = {}
    #     response = paper_connect_venue(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_paper_find(self):
    #     request = HttpRequest()
    #     request.method = 'POST'
    #     response = paper_find(request)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct
    #
    # def test_paper_detail(self):
    #     request = HttpRequest()
    #     response = paper_detail(request)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct
    #
    # def test_paper_remove_author(self):
    #     login = self.client.login(username='superuser1', password='abc123')  # test views requires admin login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.session = {}
    #     response = paper_remove_author(request)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct
    #
    # def test_paper_authors(self):
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.session = {}
    #     response = paper_authors(request)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct