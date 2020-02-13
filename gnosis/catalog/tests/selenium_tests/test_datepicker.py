from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Paper, ReadingGroup, ReadingGroupEntry
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
        #
        self.user = User.objects.create_user(username="testuser", password="12345")

        self.admin = User.objects.create_superuser(
            username="admin", password="abcdefg", email="admin@gnosis.stellargraph.io"
        )

        # Create a paper
        self.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )

        current_time = datetime.now()
        start_time = current_time.replace(hour=11, minute=0)
        end_time = current_time.replace(hour=12, minute=30)

        # this is a public group
        self.ml_group_public = ReadingGroup.objects.create(
            name="ml public",
            description="Machine Learning journal club",
            keywords="machine learning",
            is_public=True,
            videoconferencing="Dial 10101010",
            room="R101",
            day="Tuesday",
            start_time=start_time,
            end_time=end_time,
            address="11 Keith street, Dulwich Hill",
            city="Sydney",
            country="AU",
            owner=self.admin,
        )

        # add the paper to the group
        self.group_entry = ReadingGroupEntry.objects.create(
            reading_group=self.ml_group_public,
            paper=self.paper,
            proposed_by=self.admin,
        )

        # login as user by first typing the login info on the login form, then submit
        self.browser.get(self.live_server_url + '/accounts/login/')

        username = self.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys('admin')

        pwd = self.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys('abcdefg')
        self.browser.find_element_by_tag_name('form').submit()

        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jumbotron')))

        url = self.live_server_url + '/catalog/club/' + str(self.ml_group_public.id) + '/'
        self.browser.get(url)

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()

    def test_datepicker(self):
        '''test the UI of date picker with different date inputs'''
        proposed_tab = self.browser.find_element_by_id('nav-proposed-tab')
        proposed_tab.click()

        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.discuss_btn')))

        discuss_btn = self.browser.find_element_by_class_name('discuss_btn')
        discuss_btn.click()

        discuss_form = self.browser.find_element_by_id('discuss_form_container')
        self.assertTrue(discuss_form.is_displayed())

        # click on the input field
        date_input = self.browser.find_element_by_id('id_date_discussed')
        date_input.click()

        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.ID, 'ui-datepicker-div')))

        # assert the datepicker widget appears when the input is focused on
        datepicker = self.browser.find_element_by_id('ui-datepicker-div')
        self.assertTrue(datepicker.is_displayed())

        # get the second row of the calendar
        row = datepicker.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[1]

        # find a weekend option from the datepicker
        ele = row.find_elements_by_tag_name('td')[0].find_element_by_tag_name('a')
        ele.click()

        message = self.browser.find_element_by_class_name('reaction_message')
        self.assertTrue(message.is_displayed())

        # click input field again
        date_input.click()

        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.ID, 'ui-datepicker-div')))

        # get the second row of the calendar
        row = datepicker.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[1]

        # find a Tuesday option from the datepicker
        ele = row.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a')
        ele.click()

        self.assertFalse(message.is_displayed())


class FirfoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        """set the webdriver to Firefox"""
        cls.browser = webdriver.Firefox()
