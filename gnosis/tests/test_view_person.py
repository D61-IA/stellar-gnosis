from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.models import Person
from catalog.views.views_people import person_create, person_update, \
    person_detail, persons, person_find, _person_find, person_delete
from django.http import HttpRequest
from neomodel import db


class PersonViewTest(TestCase):

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

        test_user1.save()
        test_user2.save()

    # WARNING - only test the commented part when there is a way to delete the person, it's done on local machine.
    def test_person_create(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        # request.POST= {"first_name": "f", "middle_name": "m", "last_name": "l", "affiliation": "a", "website": "w"}
        # response = person_create(request)
        # self.assertEquals(response.status_code, 302)  # test if response is correct, the response is redirection
        request.method = "GET"
        response = person_create(request)
        self.assertEquals(response.status_code, 200)  # test if response is correct

    # WARNING - only test the commented part when there is a way to delete the person, it's done on local machine.
    def test_person_update(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        # request.POST= {"first_name": "fi", "middle_name": "mi", "last_name": "la", "affiliation": "af", "website": "we"}
        # response = person_update(request, 1)
        # self.assertEquals(response.status_code, 302)  # test if response is correct(redirect)
        request.method = "GET"
        response = person_update(request, 1)
        self.assertEquals(response.status_code, 200)
        response = person_update(request, -1)
        self.assertEquals(response.status_code, 200)

    def test_person_detail(self):
        request = HttpRequest()
        request.user = self.user
        request.session = {}
        response = person_detail(request, 1)
        self.assertEquals(response.status_code, 200)  # test if response is correct
        self.assertEquals(request.session["last-viewed-person"], 1)
        response = person_detail(request, -1)
        self.assertEquals(response.status_code, 200)  # test if response is correct

    def test_persons(self):
        request = HttpRequest()
        request.method = "POST"
        request.POST = {"person_name": "fi"}
        response = persons(request)
        self.assertEquals(response.status_code, 200)  # test if response is correct
        request.POST = {"person_name": "dashdaiojrqpwiokjriqwjio"}
        response = persons(request)
        # self.assertEquals(response["form"], "No results found. Please try again!")  # test if response is correct
        request.method = "GET"
        response = persons(request)
        self.assertEquals(response.status_code, 200)  # test if response is correct

    def test_person_find(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST = {"person_name": "fi"}
        response = person_find(request)
        self.assertEquals(response.status_code, 200)  # test if response is correct
        request.POST = {"person_name": "dashdaiojrqpwiokjriqwjio"}
        response = person_find(request)
        # self.assertEquals(response["form"], "No results found. Please try again!")  # test if response is correct
        request.method = "GET"
        response = person_find(request)
        self.assertEquals(response.status_code, 200)  # test if response is correct

    def test_person_find_name(self):
        person_name = "abc bcd cde"
        response = _person_find(person_name, True)
        self.assertEquals(response, None)  # test if response is correct
        person_name = "abcdefgas"
        response = _person_find(person_name, True)
        self.assertEquals(response, None)  # test if response is correct

    # def test_person_delete(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     response = person_delete(request, 1)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct

