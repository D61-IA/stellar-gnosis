import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Comment, Paper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User


class ChromeTestCase(unittest.TestCase):

    @classmethod
    def setupBrowser(cls):
        """set up testing browser"""

        cls.browser = webdriver.Chrome()

    @classmethod
    def setUpClass(cls):
        """create testing assets that are used only once"""

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

        cls.setupBrowser()

        # login as admin/user2
        cls.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/' + str(cls.paper.id) + '/')
        username = cls.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(cls.user2name)
        pwd = cls.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys(cls.user2password)
        cls.browser.find_element_by_tag_name('form').submit()
        # wait for page to load
        wait = WebDriverWait(cls.browser, 1000)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

    def setUp(self):
        """set up testing assets that will be modified in tests and global variables"""

        # create comment in setup because comment will be deleted in a test
        self.comment = Comment.objects.create(
            text="testing comment",
            created_by=self.user1,
            is_flagged=False,
            is_hidden=False,
            paper=self.paper
        )

        # go to the paper page
        self.browser.get('http://127.0.0.1:8000/catalog/paper/' + str(self.paper.id) + '/')

        # wait for page to load
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        # find and save the id of the comment as global
        self.comments = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_comment = self.comments.find_element_by_css_selector('li.list-group-item')
        self.comment_id = self.comment.id

        self.first_flag = None
        # click on its flag
        a = self.first_comment.find_element_by_tag_name('a')
        a.click()

        flag_form = self.browser.find_element_by_tag_name('form')
        violations = flag_form.find_element_by_id('id_violation')

        # select the first violation on the form
        labels = violations.find_elements_by_tag_name('label')
        input_0 = labels[0].find_element_by_tag_name('input')
        input_0.click()
        # fill in the description field
        description = flag_form.find_element_by_id('id_description')
        description.clear()
        description.send_keys('Spam description')

        flag_form.submit()

        # go to moderation page
        mod_link = self.browser.find_element_by_id('moderation_link')
        mod_link.click()

        flags = self.browser.find_element_by_css_selector('ul.list-group')
        flag_items = flags.find_elements_by_class_name('list-group-item')

        # find the flag that was just created using the comment id
        for item in flag_items:
            action = item.find_elements_by_class_name('actions')
            if len(action) > 0:
                cmt_id = action[0].get_attribute('data-commentid')
                if str(cmt_id) == str(self.comment_id):
                    self.first_flag = item
                    break

    def tearDown(self):
        """delete comment"""
        self.comment.delete()

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""
        cls.user1.delete()

        cls.user2.delete()

        cls.paper.delete()

        cls.browser.quit()


    def testRestoreComment(self):
        """test the comment restores after clicking on restore button"""

        # click on the restore button
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

        # wait for page to load
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        self.comments = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_comment = self.comments.find_element_by_css_selector('li.list-group-item')

        # test the first comment is now not flagged
        flagged_arr = self.first_comment.find_elements_by_class_name('flagged')
        self.assertEqual(len(flagged_arr), 0)

    def testDeleteComment(self):
        """test the comment is deleted after clicking on delete button"""

        # find the delete button and click
        del_button = self.first_flag.find_element_by_class_name('mod_del')
        del_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        # find action buttons
        actions = self.first_flag.find_element_by_class_name('actions')

        # test the buttons have disappeared when Ajax response is received
        self.assertEqual(actions.get_attribute('hidden'), 'true')

        # test the right response message appears
        msg = self.first_flag.find_elements_by_class_name('del_msg')
        self.assertEqual(len(msg), 1)

        # return to the paper detail page
        a = self.first_flag.find_element_by_tag_name('a')
        a.click()

        # wait for page to load
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        comments = self.browser.find_elements_by_css_selector('ul.list-group')

        # test the comment is removed
        self.assertEqual(len(comments), 0)


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set up testing browser"""

        cls.browser = webdriver.Firefox()


if __name__ == '__main__':
    # 2 (verbose): you get the help string of every test and the result
    unittest.main(verbosity=2)
