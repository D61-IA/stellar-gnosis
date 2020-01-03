from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Comment, Paper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class ChromeTestCase(StaticLiveServerTestCase):
    """test with Chrome webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set up testing browser"""

        cls.browser = webdriver.Chrome()

    @classmethod
    def setUpClass(cls):
        """create testing assets"""

        super().setUpClass()
        cls.setupBrowser()


    def setUp(self):
        """set up testing assets that will be modified in tests and global variables"""

        # create a regular user and an admin user
        user1name = 'user1'
        user1password = '12345'
        user1email = 'user1@gnosis.stellargraph.io'

        user2name = 'user2'
        user2password = 'abcde'
        user2email = 'user2@gnosis.stellargraph.io'

        self.user1 = User.objects.create_user(username=user1name, password=user1password,
                                             email=user1email)

        self.user2 = User.objects.create_superuser(username=user2name,
                                                  password=user2password,
                                                  email=user2email)

        # create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user1,
        )

        # create comment in setup because comment will be deleted in a test
        self.comment = Comment.objects.create(
            text="testing comment",
            created_by=self.user1,
            is_flagged=False,
            is_hidden=False,
            paper=self.paper
        )

        # login as admin/user2
        self.browser.get(self.live_server_url + '/accounts/login/')

        username = self.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(user2name)
        pwd = self.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys(user2password)
        self.browser.find_element_by_tag_name('form').submit()
        # confirm ajax response is received by checking correct page redirect
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

        # using get allows webdriver to wait for html to be fully ready
        self.browser.get(self.live_server_url + '/catalog/paper/' + str(self.paper.id) + '/')

        # find and save the id of the comment as global
        first_comment = self.browser.find_element_by_css_selector('#navcomment li.list-group-item')

        # click on its flag
        # test pop up flag form is shown when flag icon is clicked
        flag_clickable = first_comment.find_element_by_class_name('open_flag_dialog')
        flag_clickable.click()

        flag_form = self.browser.find_element_by_id('flag_form')
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

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.ID, 'flag_response')))
        # remove response overlay
        self.browser.find_element_by_class_name("response_ok").click()

        # scroll to bottom of page
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # go to moderation page
        mod_link = self.browser.find_element_by_id('moderation_link')
        mod_link.click()

        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        flags = self.browser.find_element_by_css_selector('ul.list-group')
        self.first_flag = flags.find_element_by_class_name('list-group-item')


    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()


    def testRestoreComment(self):
        """test the comment restores after clicking on restore button"""

        # click on the restore button
        res_button = self.first_flag.find_element_by_class_name('mod_res')
        res_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

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
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        comments = self.browser.find_element_by_css_selector('ul.list-group')
        first_comment = comments.find_element_by_css_selector('li.list-group-item')

        # test the first comment is now not flagged
        flagged_arr = first_comment.find_elements_by_class_name('flagged')
        self.assertEqual(len(flagged_arr), 0)

    def testDeleteComment(self):
        """test the comment is deleted after clicking on delete button"""

        # find the delete button and click
        del_button = self.first_flag.find_element_by_class_name('mod_del')
        del_button.click()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

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
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        comments = self.browser.find_elements_by_css_selector('ul.list-group')

        # test the comment is removed
        self.assertEqual(len(comments), 0)


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set up testing browser"""

        cls.browser = webdriver.Firefox()

