from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Paper
from bookmark.models import Bookmark
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
        """create testing assets that are used only once"""

        super().setUpClass()
        cls.setupBrowser()

    def setUp(self):
        """create testing assets"""

        # create a regular user and an admin user
        user1name = 'user1'
        user1password = '12345'
        user1email = 'user1@gnosis.stellargraph.io'

        self.user1 = User.objects.create_user(username=user1name, password=user1password,
                                              email=user1email)

        # create a paper
        self.paper1 = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user1,
        )

        # create a second paper
        self.paper2 = Paper.objects.create(
            title="2nd Best paper in the world",
            abstract="The 2nd nature of gravity.",
            download_link="https://google.com",
            created_by=self.user1
        )

        # create a bookmark for paper1
        self.bookmark1 = Bookmark.objects.create(
            paper=self.paper1,
            owner=self.user1
        )

        # create a bookmark for paper2
        self.bookmark2 = Bookmark.objects.create(
            paper=self.paper2,
            owner=self.user1
        )

        # login as user1
        self.browser.get(self.live_server_url + '/accounts/login/')
        username = self.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(user1name)
        pwd = self.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys(user1password)
        self.browser.find_element_by_tag_name('form').submit()
        # confirm ajax response is received by checking correct page redirect
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

        # go to bookmark view page
        self.browser.get(self.live_server_url + '/bookmark/')

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()

    def test_search(self):
        """test bookmark search function returns the correct links to papers"""

        # test on key shared by both papers
        search_bar = self.browser.find_element_by_id('id_bm_search')
        search_bar.send_keys('best')

        submit = self.browser.find_element_by_id('bm_submit')
        submit.click()

        # wait for page to reload
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

        # verify the correct links are present
        items = self.browser.find_elements_by_class_name('list-group-item')
        # should be only 2 bookmarks in total
        self.assertEqual(len(items), 2)

        text = items[0].find_element_by_class_name('paper_link').text
        self.assertEqual(text, 'Best paper in the world')

        text = items[1].find_element_by_class_name('paper_link').text
        self.assertEqual(text, '2nd Best paper in the world')

        # test on key unique to a paper
        search_bar = self.browser.find_element_by_id('id_bm_search')
        search_bar.send_keys('2nd')

        submit = self.browser.find_element_by_id('bm_submit')
        submit.click()

        # wait for page to reload
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

        # there should only be one item
        items = self.browser.find_element_by_class_name('list-group-item')
        text = items.find_element_by_class_name('paper_link').text
        self.assertEqual(text, '2nd Best paper in the world')

    def test_click(self):
        """test click on a bookmark redirects to its paper page"""
        links = self.browser.find_elements_by_class_name('paper_link')
        links[0].click()

        # wait for page to reload
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

        # the redirect page header should be the same as the link text
        title = self.browser.find_element_by_class_name('paper_title').text
        self.assertEqual(title, 'Best paper in the world')

    def test_remove(self):
        """test bookmark is removed when click on remove button"""
        rm_button = self.browser.find_elements_by_class_name('bm_remove')
        self.assertEqual(len(rm_button), 2)

        # remove the first paper (Best paper in the world)
        rm_button[0].click()

        # wait for page to reload
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))

        items = self.browser.find_elements_by_class_name('list-group-item')
        # should be only 1 bookmarks left
        self.assertEqual(len(items), 1)

        # check the bookmark has the right title
        self.assertEqual(items[0].find_element_by_class_name('paper_link').text, "2nd Best paper in the world")


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        cls.browser = webdriver.Firefox()