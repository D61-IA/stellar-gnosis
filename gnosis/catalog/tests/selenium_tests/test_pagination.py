from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import Paper
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
        """create testing assets"""

        # create regular users
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
        # create 3 pages of papers
        for i in range(7):
            # create a paper
            Paper.objects.create(
                title="Best paper in the world" + str(i),
                abstract="The nature of gravity.",
                download_link="https://google.com",
                created_by=self.user1,
            )

        self.url = self.live_server_url + '/catalog/papers/'
        self.browser.get(self.url)

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()


    def test_non_search(self):
        """test pagination on non-search results"""

        page_links = self.browser.find_elements_by_class_name('page_link')

        # assert the pagination has the right url links
        for idx, pl in enumerate(page_links):
            url = pl.get_attribute('href')
            self.assertEqual(url, self.live_server_url + '/catalog/papers/?page=' + str(idx+1))

        num_items = self.browser.find_elements_by_class_name('num_item')
        classes = num_items[0].get_attribute('class')
        # assert the first element has class active
        self.assertTrue('active' in classes)


    def test_search(self):
        """test pagination on search results"""

        page_links = self.browser.find_elements_by_class_name('page_link')

        search = self.browser.find_element_by_css_selector('input[name="keywords"]')
        search.clear()
        search.send_keys('world')

        form = self.browser.find_element_by_tag_name('form')
        form.submit()

        # wait for page to reload after submit
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'footer')))

        # assert the pagination has the right url links
        for idx, pl in enumerate(page_links):
            url = pl.get_attribute('href')
            self.assertEqual(url, self.live_server_url + '/catalog/paper/search/?keywords=world&page=' + str(idx+1))

        num_items = self.browser.find_elements_by_class_name('num_item')
        classes = num_items[0].get_attribute('class')
        # assert the first element has class active
        self.assertTrue('active' in classes)

    def test_previous_next(self):
        next = self.browser.find_element_by_css_selector('.page_next.desktop')
        page_link = next.find_element_by_class_name('page-link')
        self.assertEqual(page_link.get_attribute('href'), self.live_server_url + "/catalog/papers/?page=2")

        page_link.click()
        # wait for page to reload
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.pagination')))

        previous = self.browser.find_element_by_css_selector('.page_prev.desktop')
        page_link = previous.find_element_by_class_name('page-link')
        self.assertEqual(page_link.get_attribute('href'), self.live_server_url + "/catalog/papers/")


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        cls.browser = webdriver.Firefox()


