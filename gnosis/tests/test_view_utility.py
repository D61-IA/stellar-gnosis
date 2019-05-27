from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.views.views import build
from django.http import HttpRequest


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_form_paper
class UtilityViewTest(TestCase):
    def setUp(self):
        # Create a superuser
        test_superuser1 = User.objects.create_superuser(username='superuser1', password='abc123', email='superuser123@gnosis.com')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

        test_superuser1.save()

    # def test_build(self):
    #     login = self.client.login(username='superuser1', password='abc123')
    #     request = HttpRequest()
    #     request.user = self.user
    #     response = build(request)
    #     self.assertEquals(response.status_code, 200)