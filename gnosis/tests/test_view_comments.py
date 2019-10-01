from django.test import TestCase
from django.contrib.auth.models import User, Permission
from catalog.models import Comment
from catalog.views.views import comment_create, comments, comment_detail, comment_update
from django.http import HttpRequest


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_view_comment
class CommentViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_superuser1 = User.objects.create_superuser(username='superuser1', password='abc123', email='superuser123@gnosis.com')
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

        test_user1.save()
        test_user2.save()
        test_superuser1.save()

    # def test_comment_create(self):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = comment_create(request)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct
    #     self.assertTrue("Share your thoughts!" in str(response.content))
    #
    # def test_comment_update(self, id):
    #     login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')  # test views requires login
    #     request = HttpRequest()
    #     request.user = self.user
    #     request.method = 'POST'
    #     request.session = {}
    #     response = comment_update(request, id)
    #     self.assertEquals(response.status_code, 200)  # test if response is correct
    #
    # def test_comments(self):
    #     login = self.client.login(username='superuser1', password='abc123')
    #     request = HttpRequest()
    #     request.user = self.user
    #     response = comments(request)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_comment_detail(self):
    #     request = HttpRequest()
    #     request.user = self.user
    #     response = comment_detail(request)
    #     self.assertEquals(response.status_code, 200)