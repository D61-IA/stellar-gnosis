import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import CommentFlag, Comment, Paper
from catalog.forms import FlaggedCommentForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User


class ChromeTestCase(unittest.TestCase):

    def setupBrowser(self):
        """set up testing browser"""

        self.browser = webdriver.Chrome()

    # def createUsers(self):
    #     """create two users, user2 as admin whose info will be used for logging in"""
    #
    #     self.username = 'user1'
    #     self.userpassword = '12345'
    #     self.useremail = 'user1@gnosis.stellargraph.io'
    #
    #     self.user2name = 'user2'
    #     self.user2password = 'abcde'
    #     self.user2email = 'user2@gnosis.stellargraph.io'
    #
    #     self.user = User.objects.create_user(username=self.username, password=self.userpassword,
    #                                          email=self.useremail)
    #
    #     # create user 2 who is an admin
    #     self.user2 = User.objects.create_superuser(username=self.user2name,
    #                                                password=self.user2password,
    #                                                email=self.user2email)

    @classmethod
    def setUpClass(cls):

        # create a regular user and an admin user
        cls.user1name = 'user1'
        cls.user1password = '12345'
        cls.user1email = 'user1@gnosis.stellargraph.io'

        cls.user2name = 'user2'
        cls.user2password = 'abcde'
        cls.user2email = 'user2@gnosis.stellargraph.io'

        cls.user1 = User.objects.create_user(username=cls.user1name, password=cls.user1password,
                                             email=cls.user1email)

        cls.user2 = User.objects.create_superuser(username=cls.user2name,
                                                  password=cls.user2password,
                                                  email=cls.user2email)
        # create a paper
        cls.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=cls.user1,
        )

    def setUp(self):

        # in setup because comment will be deleted in a test
        self.comment = Comment.objects.create(
            text="testing comment",
            created_by=self.user1,
            is_flagged=False,
            is_hidden=False,
            paper=self.paper
        )

        self.setupBrowser()
        # login as admin
        self.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/' + str(self.paper.id) + '/')
        username = self.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(self.user2name)

        pwd = self.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys(self.user2password)

        self.browser.find_element_by_tag_name('form').submit()

        self.comments = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_comment = self.comments.find_element_by_css_selector('li.list-group-item')
        self.comment_id = self.comment.id

        self.first_flag = None

        a = self.first_comment.find_element_by_tag_name('a')
        a.click()

        # completing and submitting a flag form
        flag_form = self.browser.find_element_by_tag_name('form')

        violations = flag_form.find_element_by_id('id_violation')
        labels = violations.find_elements_by_tag_name('label')
        input_0 = labels[0].find_element_by_tag_name('input')
        input_0.click()

        description = flag_form.find_element_by_id('id_description')
        description.clear()
        description.send_keys('Spam description')

        flag_form.submit()

        # go to moderation page
        mod_link = self.browser.find_element_by_id('moderation_link')
        mod_link.click()

        flags = self.browser.find_element_by_css_selector('ul.list-group')
        flag_items = flags.find_elements_by_class_name('list-group-item')
        for item in flag_items:
            action = item.find_elements_by_class_name('actions')
            if len(action) > 0:
                cmt_id = action[0].get_attribute('data-commentid')
                if str(cmt_id) == str(self.comment_id):
                    self.first_flag = item
                    break

    def tearDown(self):
        self.comment.delete()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

        cls.admin.delete()

        cls.paper.delete()

    def testRestoreComment(self):
        res_button = self.first_flag.find_element_by_class_name('mod_res')
        res_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        actions = self.first_flag.find_element_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(actions.get_attribute('hidden'), 'true')

        # assert the right response button
        msg = self.first_flag.find_elements_by_class_name('res_msg')
        self.assertEqual(len(msg), 1)

        # return to the paper detail page
        a = self.first_flag.find_element_by_tag_name('a')
        a.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        self.comments = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_comment = self.comments.find_element_by_css_selector('li.list-group-item')

        flagged_arr = self.first_comment.find_elements_by_class_name('flagged')
        self.assertEqual(len(flagged_arr), 0)

    def testDeleteComment(self):

        del_button = self.first_flag.find_element_by_class_name('mod_del')
        del_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        actions = self.first_flag.find_element_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(actions.get_attribute('hidden'), 'true')

        # assert the right response button
        msg = self.first_flag.find_elements_by_class_name('del_msg')
        self.assertEqual(len(msg), 1)

        # return to the paper detail page
        a = self.first_flag.find_element_by_tag_name('a')
        a.click()

        self.comments = self.browser.find_elements_by_css_selector('ul.list-group')

        self.assertEqual(len(self.comments), 0)
        self.browser.quit()


class FirefoxTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.usrname = 'testuser130'
        cls.adminname = 'admin30'

        cls.user = User.objects.create_user(username=cls.usrname, password="12345")

        cls.admin = User.objects.create_superuser(username=cls.adminname,
                                                  password='abcdefg',
                                                  email="admin@gnosis.stellargraph.io")
        # Create a paper
        cls.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=cls.user,
        )

    def setUp(self):

        self.comment = Comment.objects.create(
            text="testing comment",
            created_by=self.user,
            is_flagged=False,
            is_hidden=False,
            paper=self.paper
        )

        self.browser = webdriver.Firefox()
        # login as admin
        self.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/' + str(self.paper.id) + '/')
        username = self.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(self.adminname)

        pwd = self.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys('abcdefg')

        self.browser.find_element_by_tag_name('form').submit()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        self.comments = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_comment = self.comments.find_element_by_css_selector('li.list-group-item')
        self.comment_id = self.comment.id

        self.first_flag = None

        a = self.first_comment.find_element_by_tag_name('a')
        a.click()

        # completing and submitting a flagging form
        flag_form = self.browser.find_element_by_tag_name('form')

        violations = flag_form.find_element_by_id('id_violation')
        labels = violations.find_elements_by_tag_name('label')
        input_0 = labels[0].find_element_by_tag_name('input')
        input_0.click()

        description = flag_form.find_element_by_id('id_description')
        description.clear()
        description.send_keys('Spam description')

        flag_form.submit()

        # go to moderation page
        mod_link = self.browser.find_element_by_id('moderation_link')
        mod_link.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        flags = self.browser.find_element_by_css_selector('ul.list-group')
        flag_items = flags.find_elements_by_class_name('list-group-item')
        for item in flag_items:
            action = item.find_elements_by_class_name('actions')
            if len(action) > 0:
                cmt_id = action[0].get_attribute('data-commentid')

                if str(cmt_id) == str(self.comment_id):
                    self.first_flag = item
                    break

    def tearDown(self):
        self.comment.delete()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

        cls.admin.delete()

        cls.paper.delete()

    def testRestoreComment(self):
        res_button = self.first_flag.find_element_by_class_name('mod_res')
        res_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        actions = self.first_flag.find_element_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(actions.get_attribute('hidden'), 'true')

        # assert the right response button
        msg = self.first_flag.find_elements_by_class_name('res_msg')
        self.assertEqual(len(msg), 1)

        # return to the paper detail page
        a = self.first_flag.find_element_by_tag_name('a')
        a.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        self.comments = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_comment = self.comments.find_element_by_css_selector('li.list-group-item')

        flagged_arr = self.first_comment.find_elements_by_class_name('flagged')
        self.assertEqual(len(flagged_arr), 0)

    def testDeleteComment(self):

        del_button = self.first_flag.find_element_by_class_name('mod_del')
        del_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        actions = self.first_flag.find_element_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(actions.get_attribute('hidden'), 'true')

        # assert the right response button
        msg = self.first_flag.find_elements_by_class_name('del_msg')
        self.assertEqual(len(msg), 1)

        # return to the paper detail page
        a = self.first_flag.find_element_by_tag_name('a')
        a.click()

        self.comments = self.browser.find_elements_by_css_selector('ul.list-group')

        self.assertEqual(len(self.comments), 0)
        self.browser.quit()


#
# class EdgeTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.browser = webdriver.Edge()
#         self.addCleanup(self.browser.quit)
#
#     def testPageTitle(self):
#         self.browser.get('http://www.google.com')
#         self.assertIn('Google', self.browser.title)


if __name__ == '__main__':
    unittest.main(verbosity=2)
