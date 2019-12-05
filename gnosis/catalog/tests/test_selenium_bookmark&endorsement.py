import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Comment, Paper, Endorsement
from bookmark.models import Bookmark
from catalog.forms import FlaggedCommentForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User

class ChromeTestCase(unittest.TestCase):
    """test with Chrome webdriver"""

    @classmethod
    def setUpClass(cls):
        """set up testing assets and log in"""

        # create users
        # create two users, user2's info will be used for logging in
        cls.user1name = 'user1'
        cls.user1password = '12345'
        cls.user1email = 'user1@gnosis.stellargraph.io'

        cls.user2name = 'user2'
        cls.user2password = 'abcde'
        cls.user2email = 'user2@gnosis.stellargraph.io'

        cls.user1 = User.objects.create_user(username=cls.user1name, password=cls.user1password,
                                             email=cls.user1email)

        cls.user2 = User.objects.create_user(username=cls.user2name,
                                                   password=cls.user2password,
                                                   email=cls.user2email)
        # create a paper

        # login

        # set up global variables


    def setupBrowser(self):
        """set up testing driver"""
        self.browser = webdriver.Chrome


    # def testEndorsement:
    #     """test endorse/undo endorse and related functionality"""
    #
    #
    # def testBookmark:
    #     """test bookmark/undo bookmark and related functionality"""


