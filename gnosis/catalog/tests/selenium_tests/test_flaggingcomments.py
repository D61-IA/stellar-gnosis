from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Comment, Paper
from catalog.forms import FlaggedCommentForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class ChromeTestCase(StaticLiveServerTestCase):
    """test with Chrome webdriver"""

    def fillFlagForm(self, flag_form):
        """fill in the flag form"""

        # select the first violation
        input_0 = flag_form.find_element_by_id('id_violation_0')
        input_0.click()
        # find description text area, empty the field and insert text
        description_elements = flag_form.find_element_by_id('id_description')
        description_elements.clear()
        description_elements.send_keys('violation description')

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
        """create testing assets, log in and set up global variables"""

        # create two users, user2's info will be used for logging in
        user1name = 'user1'
        user1password = '12345'
        user1email = 'user1@gnosis.stellargraph.io'

        user2name = 'user2'
        user2password = 'abcde'
        user2email = 'user2@gnosis.stellargraph.io'

        self.user1 = User.objects.create_user(username=user1name, password=user1password,
                                             email=user1email)

        self.user2 = User.objects.create_user(username=user2name,
                                                   password=user2password,
                                                   email=user2email)

        # create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user1,
        )

        # create a comment
        self.comment = Comment.objects.create(
            text="testing comment",
            created_by=self.user1,
            is_flagged=False,
            is_hidden=False,
            paper=self.paper
        )

        # login as user by first typing the login info on the login form, then submit
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
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jumbotron')))

        # using get allows webdriver to wait for html to be fully ready
        self.paper_url = self.live_server_url + '/catalog/paper/' + str(self.paper.id) + '/'
        self.browser.get(self.paper_url)

        # remove cookies popup
        self.browser.execute_script("return document.getElementsByClassName('cookiealert')[0].remove()")

        comment_container = self.browser.find_element_by_css_selector('ul.list-group')
        # there should be only one comment in this fictional paper
        self.first_comment = comment_container.find_element_by_css_selector('li.list-group-item')

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()

    def test_flaggingcomments(self):
        """test all actions for flagging a comment"""

        first_comment = self.first_comment
        browser = self.browser
        flag_form_container = browser.find_element_by_id('flag_form_container')

        # test the flag is an outlined flag for unflagged comment
        text = first_comment.find_element_by_class_name('material-icons').text
        self.assertEqual(text, 'outlined_flag')

        # test pop up flag form is shown when flag icon is clicked
        flag_clickable = first_comment.find_element_by_class_name('open_flag_dialog')
        flag_clickable.click()
        a1 = flag_form_container.get_attribute('hidden')
        self.assertEqual(a1, None)

        # test flag form has the right fields
        flag_form = browser.find_element_by_id('flag_form')
        violations = flag_form.find_element_by_id('id_violation')
        labels = violations.find_elements_by_tag_name('label')
        true_violations = FlaggedCommentForm().fields['violation'].choices
        true_labels = [v[1] for v in true_violations]

        # test radio buttons have the right labels.
        for i in range(len(labels)):
            self.assertEqual(true_labels[i], labels[i].text)

        # test the form has one description field
        description = flag_form.find_elements_by_tag_name('textarea')
        self.assertEqual(len(description), 1)
        desc_id = description[0].get_attribute('id')
        self.assertEqual(desc_id, 'id_description')

        # find first select option and select
        self.fillFlagForm(flag_form)

        # test the cancel button works
        flag_form.find_element_by_tag_name('button').click()
        self.assertEqual(flag_form_container.get_attribute('hidden'), 'true')

        # test the choice and description are cleared after clicking cancel button
        choice = flag_form.find_element_by_id('id_violation_0')
        self.assertFalse(choice.is_selected())
        text = flag_form.find_element_by_id('id_description')
        self.assertFalse(text.get_attribute('value'))

        # reopen the form
        flag_clickable.click()
        self.fillFlagForm(flag_form)

        flag_form.submit()
        # wait for Ajax response
        wait = WebDriverWait(browser, 10)
        wait.until(EC.visibility_of_element_located((By.ID, 'response_msg')))

        # after submit, test flag form is hidden
        a1 = browser.find_element_by_id('flag_form_container').get_attribute('hidden')
        self.assertEqual(a1, 'true')
        # test flag_response is unhidden after successful submit
        flag_response = browser.find_element_by_id('response_msg')
        self.assertEqual(flag_response.get_attribute('hidden'), None)

        self.browser.find_element_by_class_name("response_ok").click()

        # test the flagged comment has a filled flag icon attached
        arr = first_comment.find_elements_by_class_name("flagged")
        self.assertEqual(len(arr), 1)
        arr = first_comment.find_elements_by_class_name("material-icons")
        self.assertEqual(arr[0].text, "flag")

class FirfoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set the webdriver to Firefox"""
        cls.browser = webdriver.Firefox()
