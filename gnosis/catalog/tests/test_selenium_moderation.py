import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import CommentFlag, Comment, Paper
from catalog.forms import FlaggedCommentForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User


class GoogleTestCase(unittest.TestCase):

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

        self.browser = webdriver.Chrome()
        # login as admin
        self.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/' + str(self.paper.id) + '/')
        username = self.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(self.adminname)

        pwd = self.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys('abcdefg')

        self.browser.find_element_by_tag_name('form').submit()

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

        flags = self.browser.find_element_by_css_selector('ul.list-group')
        flag_items = flags.find_elements_by_class_name('list-group-item')
        for item in flag_items:
            action = item.find_elements_by_class_name('actions')
            if len(action) > 0:
                cmt_id = action[0].get_attribute('data-commentid')
                print(cmt_id)
                print(self.comment_id)
                if str(cmt_id) == str(self.comment_id):
                    print("this is true!")
                    self.first_flag = item
                    break


        print(self.first_flag is None)

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

        actions = self.first_flag.find_elements_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(len(actions), 0)

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

        actions = self.first_flag.find_elements_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(len(actions), 0)

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
                print(cmt_id)
                print(self.comment_id)
                if str(cmt_id) == str(self.comment_id):
                    print("this is true!")
                    self.first_flag = item
                    break


        print(self.first_flag is None)

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

        actions = self.first_flag.find_elements_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(len(actions), 0)

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

        actions = self.first_flag.find_elements_by_class_name('actions')

        # assert the buttons have disappeared when Ajax response is received
        self.assertEqual(len(actions), 0)

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
