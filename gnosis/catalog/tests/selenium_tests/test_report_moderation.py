from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Paper
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

        # report the paper
        report_btn = self.browser.find_element_by_id('report_error')
        report_btn.click()
        error_form = self.browser.find_element_by_id('error_form')
        self.fillForm(error_form)
        error_form.submit()

        # wait for Ajax response
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.ID, 'response_msg')))

        # remove response overlay
        self.browser.find_element_by_class_name("response_ok").click()

        # go to the moderation page
        self.browser.get(self.live_server_url + '/catalog/moderation/papers/reports/')
        self.report = self.browser.find_element_by_class_name('list-group-item')


    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()


    def testResolveComment(self):
        """test the comment restores after clicking on restore button"""

        # click on the resolve button
        resl_button = self.report.find_element_by_class_name('mod_resl')
        resl_button.click()

        # wait for Ajax response
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'res_msg')))

        # assert the resolved message is shown
        msg = self.report.find_elements_by_class_name('res_msg')
        self.assertEqual(len(msg), 1)

        # click again on the resolve button
        resl_button.click()

        # wait for Ajax response
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'del_msg')))

        # assert the unresolved message is shown
        msg = self.report.find_elements_by_class_name('del_msg')
        self.assertEqual(len(msg), 1)

    def testDeleteReport(self):
        """test the comment is deleted after clicking on delete button"""

        # find the delete button and click
        del_button = self.report.find_element_by_class_name('mod_del')
        del_button.click()

        # wait for Ajax response
        WebDriverWait(self.browser, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'actions')))

        # find action buttons
        actions = self.report.find_element_by_class_name('actions')
        # test the buttons have disappeared when Ajax response is received
        self.assertEqual(actions.get_attribute('hidden'), 'true')

        # find state
        state = self.report.find_element_by_class_name('state')
        # test the state has disappeared when Ajax response is received
        self.assertEqual(state.get_attribute('hidden'), 'true')

        # test the right response message appears
        msg = self.report.find_elements_by_class_name('del_msg')
        self.assertEqual(len(msg), 2)


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set up testing browser"""

        cls.browser = webdriver.Firefox()

