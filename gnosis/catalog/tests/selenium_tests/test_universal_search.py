from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

from bookmark.models import Bookmark
from catalog.models import Paper, Person, Code, Venue, Dataset, ReadingGroup, Endorsement
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

        self.user = User.objects.create_user(username=user1name, password=user1password,
                                             email=user1email)

        # create a paper
        self.paper1 = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=self.user,
        )
        # create a second paper
        self.paper2 = Paper.objects.create(
            title="2nd Best paper in the world",
            abstract="The 2nd nature of gravity.",
            download_link="https://google.com",
            created_by=self.user
        )

        self.person1 = Person.objects.create(name='Gregg Zhao', created_by=None)
        self.person2 = Person.objects.create(name='Zhenghao Zhao', created_by=self.user)

        # Create a Code repo entry
        self.code1 = Code.objects.create(
            name="StellarGraph",
            description="Python library for graph machine learning.",
            website="https://stellargraph.io",
            keywords="graph machine learning",
            created_by=self.user,
        )
        # Create a Code repo entry
        self.code2 = Code.objects.create(
            name="StellarGraph copy",
            description="Graph theory (network) library for visualisation and analysis.",
            website="https://github.com/cytoscape/cytoscape.js",
            keywords="visualisation and analysis",
            created_by=self.user,
        )

        self.venue1 = Venue.objects.create(
            name="ICCV",
            publication_year=2017,
            publication_month="July",
            venue_type="Conference",
            peer_reviewed="Yes",
            website="http://openaccess.thecvf.com/ICCV2017.py",
            created_by=self.user,
        )
        self.venue2 = Venue.objects.create(
            name="ICCV copy",
            publication_year=2017,
            publication_month="July",
            venue_type="Conference",
            peer_reviewed="Yes",
            website="https://dl.acm.org/",
            created_by=self.user,
        )

        self.dataset1 = Dataset.objects.create(
            name="Cora",
            keywords="network, citation graph",
            description="A citation network dataset.",
            publication_year=2015,
            publication_month="October",
            dataset_type="Network",
            website="https://scholar.google.com",
            created_by=self.user,
        )
        self.dataset2 = Dataset.objects.create(
            name="Cora copy",
            keywords="fish toxicity",
            description="QSAR fish toxicity Data Set.",
            publication_year=2019,
            publication_month="September",
            dataset_type="Network",
            website="https://archive.ics.uci.edu/ml/datasets/QSAR+fish+toxicity",
            created_by=self.user,
        )

        current_time = datetime.now()
        start_time = current_time.replace(hour=11, minute=0)
        end_time = current_time.replace(hour=12, minute=30)

        self.club1 = ReadingGroup.objects.create(
            name="public club",
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
            owner=self.user,
        )
        self.club2 = ReadingGroup.objects.create(
            name="test club",
            description="Machine Learning journal club",
            keywords="algorithm learning",
            is_public=True,
            videoconferencing="Dial 10101010",
            room="R101",
            day="Tuesday",
            start_time=start_time,
            end_time=end_time,
            address="11 Keith street, Dulwich Hill",
            city="Sydney",
            country="AU",
            owner=self.user,
        )

        self.bookmark1 = Bookmark.objects.create(
            paper=self.paper1,
            owner=self.user
        )

        self.bookmark2 = Bookmark.objects.create(
            paper=self.paper2,
            owner=self.user
        )

        # create a endorsement for paper1
        self.endorsement1 = Endorsement.objects.create(
            paper=self.paper1,
            user=self.user
        )

        # create a endorsement for paper2
        self.endorsement2 = Endorsement.objects.create(
            paper=self.paper2,
            user=self.user
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
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jumbotron')))

    @classmethod
    def tearDownClass(cls):
        """delete testing assets and quit webdriver and browser"""
        super().tearDownClass()
        cls.browser.quit()

    def search(self, text_both, text_unique):
        form = self.browser.find_element_by_id('universal_search')
        search_box = form.find_element_by_tag_name('input')
        search_box.clear()
        search_box.send_keys(text_both)
        submit_btn = form.find_element_by_tag_name('button')
        submit_btn.click()
        # wait for page to reload
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))
        # verify the correct links are present
        items = self.browser.find_elements_by_class_name('list-group-item')
        # should be only 2 search results in total
        self.assertEqual(len(items), 2)

        form = self.browser.find_element_by_id('universal_search')
        search_box = form.find_element_by_tag_name('input')
        search_box.clear()
        search_box.send_keys(text_unique)
        submit_btn = form.find_element_by_tag_name('button')
        submit_btn.click()
        # wait for page to reload
        WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.card-header')))
        # verify the correct links are present
        items = self.browser.find_elements_by_class_name('list-group-item')
        # should be only 2 search results in total
        self.assertEqual(len(items), 1)

    def test_search_paper(self):
        self.browser.get(self.live_server_url + '/catalog/papers/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'paper')
        self.search("best", "2nd")

    def test_search_person(self):
        self.browser.get(self.live_server_url + '/catalog/authors/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'person')
        self.search("Zhao", "Zhenghao")
    #
    def test_search_venue(self):
        self.browser.get(self.live_server_url + '/catalog/venues/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'venue')
        self.search("ICCV", "copy")

    def test_search_dataset(self):
        self.browser.get(self.live_server_url + '/catalog/datasets/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'dataset')
        self.search("Cora", "copy")

    def test_search_code(self):
        self.browser.get(self.live_server_url + '/catalog/codes/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'code')
        self.search("StellarGraph", "copy")

    def test_search_group(self):
        self.browser.get(self.live_server_url + '/catalog/clubs/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'club')
        self.search("learning", "algorithm")

    def test_search_bookmark(self):
        self.browser.get(self.live_server_url + '/bookmark/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'bookmark')
        self.search("best", "2nd")

    def test_search_endorsement(self):
        self.browser.get(self.live_server_url + '/catalog/endorsements/')
        select = self.browser.find_element_by_id('universal_select')
        self.assertEqual(select.get_attribute('value'), 'endorsement')
        self.search("best", "2nd")


    def test_dropdown(self):
        self.browser.get(self.live_server_url + '/catalog/papers/')
        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="person"]').click()
        self.search("Zhao", "Zhenghao")

        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="venue"]').click()
        self.search("ICCV", "copy")

        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="dataset"]').click()
        self.search("Cora", "copy")

        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="code"]').click()
        self.search("StellarGraph", "copy")

        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="club"]').click()
        self.search("learning", "algorithm")

        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="bookmark"]').click()
        self.search("best", "2nd")

        select = self.browser.find_element_by_id('universal_select')
        select.find_element_by_css_selector('option[value="endorsement"]').click()
        self.search("best", "2nd")


class FirefoxTestCase(ChromeTestCase):
    """test with Firefox webdriver"""

    @classmethod
    def setupBrowser(cls):
        cls.browser = webdriver.Firefox()
