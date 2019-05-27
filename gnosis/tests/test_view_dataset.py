from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.models import Dataset
from catalog.views.views import dataset_create, dataset_detail, datasets, dataset_update, \
    dataset_find
from django.http import HttpRequest


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_form_paper
class DatasetViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

        test_user1.save()
        test_user2.save()

    # def test_dataset_create(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = dataset_create(request)
    #     self.assertEquals(response.status_code, 200)        # test if response is correct
    #     self.assertTrue("New Dataset" in str(response.content) and "Name*" in str(response.content)
    #                     and "Keywords*" in str(response.content) and "Description*" in str(response.content))
    #
    # def test_dataset_update(self,  id):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = dataset_update(request, id)
    #     self.assertEquals(response.status_code, 200)        # test if response is correct
    #
    # def test_dataset_detail(self, id):
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.session = {}
    #     response = dataset_detail(request, id)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_datasets(self):
    #     request = HttpRequest()
    #     request.user = self.user
    #     response = datasets(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_dataset_find(self):
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST', 'GET'
    #     response = dataset_find(request)
    #     self.assertEquals(response.status_code, 200)


