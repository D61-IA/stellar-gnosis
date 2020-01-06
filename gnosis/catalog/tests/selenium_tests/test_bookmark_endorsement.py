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
        """create testing assets that are used only once"""

        super().setUpClass()
        cls.setupBrowser()

    def setUp(self):
        """create testing assets"""

        # create a regular user and an admin user
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

        # login as user2
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

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""

        super().tearDownClass()
        cls.browser.quit()

    # attr_dic: {attr0_name: attr0_value, ...}
    def assert_element(self, ele, classes, attr_dic, text):
        """test an element has the right classes, attributes and innerText"""
        ele_classes = ele.get_attribute("class")
        for c in ele_classes.split():
            self.assertTrue(c in classes)

        for key, value in attr_dic.items():
            self.assertEqual(ele.get_attribute(key), value)

        self.assertEqual(ele.text, text)


    def assert_light_off(self):
        """test lightbulb has the right attribute when it's not endorsed"""

        self.endorsement_create = self.browser.find_element_by_id("e_create")
        icon_bulb = self.endorsement_create.find_element_by_class_name("material-icons")

        self.assert_element(ele=icon_bulb, classes=["material-icons", "light_off"],
                            attr_dic={"data-toggle": "tooltip", "title": "add endorsement"}, text="lightbulb_outline")

    def assert_light_on(self):
        """test lightbulb has the right attribute when it's endorsed"""

        self.endorsement_create = self.browser.find_element_by_id("e_create")
        icon_bulb = self.endorsement_create.find_element_by_class_name("material-icons")

        self.assert_element(ele=icon_bulb, classes=["material-icons", "light_on"],
                            attr_dic={"data-toggle": "tooltip", "title": "remove endorsement"}, text="lightbulb")

    def assert_bookmark_off(self):
        """test bookmark icon has the right attribute when it's not bookmarked"""

        self.bookmark_create = self.browser.find_element_by_id("b_create")
        icon_bm = self.bookmark_create.find_element_by_class_name("material-icons")

        self.assert_element(ele=icon_bm, classes=["material-icons", "bm_off"],
                            attr_dic={"data-toggle": "tooltip", "title": "add bookmark"}, text="bookmark_border")

    def assert_bookmark_on(self):
        """test bookmark icon has the right attribute when it's not bookmarked"""

        self.bookmark_create = self.browser.find_element_by_id("b_create")
        icon_bm = self.bookmark_create.find_element_by_class_name("material-icons")

        self.assert_element(ele=icon_bm, classes=["material-icons", "bm_on"],
                            attr_dic={"data-toggle": "tooltip", "title": "remove bookmark"}, text="bookmark")

    def test_endorsement(self):
        """test endorse functionality"""

        # before click
        # test it is an outlined lightbulb
        self.assert_light_off()

        # after first click
        # test it is a lighting lightbulb
        self.endorsement_create.click()

        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'light_on')))
        self.assert_light_on()

        # after second click
        # test it goes back to an outlined lightbulb
        self.endorsement_create.click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'light_off')))
        self.assert_light_off()

    def test_bookmark(self):
        """test bookmark functionality"""

        # before click
        # test it is an outlined bookmark
        self.assert_bookmark_off()

        # after first click
        # test it is a filled bookmark
        self.bookmark_create.click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'bm_on')))
        self.assert_bookmark_on()

        # after second click
        # test it goes back to an outlined bookmark
        self.bookmark_create.click()
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'bm_off')))
        self.assert_bookmark_off()


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        cls.browser = webdriver.Firefox()
