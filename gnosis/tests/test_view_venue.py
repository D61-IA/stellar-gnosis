from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.models import Venue
from catalog.views.views import venue_create, venues, venue_detail, venue_find, venue_update
from django.http import HttpRequest

# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_form_paper
class VenueViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

        test_user1.save()
        test_user2.save()

    # def test_venue_create(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = venue_create(request)
    #     self.assertEquals(response.status_code, 200)        # test if response is correct
    #     self.assertTrue("New Venue" in str(response.content) and "Name*" in str(response.content)
    #                     and "Type*" in str(response.content) and "Peer Reviewed*" in str(response.content))
    #
    # def test_venue_update(self, id):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = venue_update(request, id)
    #     self.assertEquals(response.status_code, 200)        # test if response is correct
    #
    # def test_venues(self):
    #     request = HttpRequest()
    #     request.user = self.user
    #     response = venues(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_venue_detail(self, id):
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.session = {}
    #     response = venue_detail(request, id)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_venue_find(self):
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     response = venue_find(request)
    #     self.assertEquals(response.status_code, 200)