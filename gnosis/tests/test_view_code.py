from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.models import Code
from catalog.views.views_codes import code_create, code_update, code_find, codes, code_detail
from django.http import HttpRequest


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_view_code
class CodeViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

        test_user1.save()
        test_user2.save()

    # Warning: Do not test commented parts unless it can be deleted later. The test is done on a local machine
    def test_code_create(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        # request.POST = {"website":"W", "keywords":"K", "description":"D"}
        # response = code_create(request)
        # self.assertEquals(response.status_code, 302)        # test if response is correct
        request.method = "GET"
        response = code_create(request)
        self.assertEquals(response.status_code, 200)

    def test_codes(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST = {"keywords": "K"}
        response = codes(request)
        self.assertEquals(response.status_code, 200)
        request.method = "GET"
        response = codes(request)
        self.assertEquals(response.status_code, 200)

    # Warning: Do not test commented parts unless it can be deleted later. The test is done on a local machine
    def test_code_update(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        response = code_update(request, 1)
        self.assertEquals(response.status_code, 200)
        request.method = 'POST'
        # request.POST = {"website":"www.google.com", "keywords":"machine learning", "description":"D"}
        # response = code_update(request, -1)   # failure scenario
        # self.assertEquals(response.status_code, 302)
        request.method = 'GET'
        response = code_update(request, 1)
        self.assertEquals(response.status_code, 200)
        response = code_update(request, -1)
        self.assertEquals(response.status_code, 200)

    # Warning: Do not test commented parts unless it can be deleted later. The test is done on a local machine
    def test_code_find(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        # request.POST = {"website": "www.google.com", "keywords": "K", "description": "D"}
        response = code_find(request)
        self.assertEquals(response.status_code, 200)
        # request.POST = {"website": "www.google.com", "keywords": "asasfasdqweda", "description": "D"}
        # response = code_find(request)
        # self.assertEquals(response.status_code, 200)
        request.method = "GET"
        response = code_find(request)
        self.assertEquals(response.status_code, 200)

    def test_code_detail(self):
        request = HttpRequest()
        request.session = {}
        response = code_detail(request, 1)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(request.session["last-viewed-code"] == 1)
        response = code_detail(request, -1)
        self.assertEquals(response.status_code, 200)
