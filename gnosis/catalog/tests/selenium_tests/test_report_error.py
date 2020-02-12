import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Paper
from catalog.forms import PaperReportForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class ChromeTestCase(StaticLiveServerTestCase):
    """test with Chrome webdriver"""

    def fillForm(self, form):
        """fill the form"""

        # select the first violation
        input_0 = form.find_element_by_id('id_error_type_0')
        input_0.click()
        # find description text area, empty the field and insert text
        description_elements = form.find_element_by_id('id_description_fb')
        description_elements.clear()
        description_elements.send_keys('Title error description')

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
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jumbotron')))

        # using get allows webdriver to wait for html to be fully ready
        self.paper_url = self.live_server_url + '/catalog/paper/' + str(self.paper.id) + '/'
        self.browser.get(self.paper_url)

        # remove cookies popup
        self.browser.execute_script("return document.getElementsByClassName('cookiealert')[0].remove()")


    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()

    def test_reportError(self):
        """test all actions for report a paper error"""

        browser = self.browser
        error_form_container = browser.find_element_by_id('error_form_container')

        # test pop up form is shown after clicking on report button
        report_btn = browser.find_element_by_id('report_error')
        report_btn.click()
        a1 = error_form_container.get_attribute('hidden')
        self.assertEqual(a1, None)

        # test the form has the right fields
        error_form = browser.find_element_by_id('error_form')
        parts = error_form.find_element_by_id('id_error_type')
        labels = parts.find_elements_by_tag_name('label')

        true_labels = [c[1] for c in PaperReportForm().fields['error_type'].choices]

        # test radio buttons have the right labels and they are in the right order.
        for i in range(len(labels)-1):
            self.assertEqual(true_labels[i], labels[i].text)

        # assert the venue has not a label because it is hidden in this case (paper not connected to venue)
        self.assertEqual(labels[-1].text, '')

        # test the form has one description field
        description = error_form.find_elements_by_tag_name('textarea')
        self.assertEqual(len(description), 1)

        # find first select option and select
        self.fillForm(error_form)

        # test the cancel button works
        error_form.find_element_by_css_selector('button.form_btn').click()
        self.assertEqual(error_form_container.get_attribute('hidden'), 'true')

        # reopen the form
        report_btn.click()

        # test the choice and description are cleared after clicking cancel button
        choice = error_form.find_element_by_id('id_error_type_0')
        self.assertFalse(choice.is_selected())
        text = error_form.find_element_by_id('id_description_fb')
        self.assertFalse(text.get_attribute('value'))

        self.fillForm(error_form)

        error_form.submit()
        # wait for Ajax response
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'response_msg_container')))

        # after submit, test form is hidden
        a1 = browser.find_element_by_id('error_form_container').get_attribute('hidden')
        self.assertEqual(a1, 'true')
        # test response message is unhidden after successful submit
        response = browser.find_element_by_id('response_msg_container')
        self.assertEqual(response.get_attribute('hidden'), None)

        self.browser.find_element_by_class_name("response_ok").click()

class FirfoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set the webdriver to Firefox"""
        cls.browser = webdriver.Firefox()
