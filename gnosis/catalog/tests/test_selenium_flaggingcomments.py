import unittest
from selenium import webdriver

class GoogleTestCase(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.addCleanup(self.browser.quit)

    def testPageTitle(self):
        self.browser.get('http://127.0.0.1:8000/catalog/paper/1/')
        count = self.browser.execute_script("return paper_count")
        self.assertIn('Gnosis Research Paper Management', self.browser.title)

    

class FirefoxTestCase(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.addCleanup(self.browser.quit)

    def testPageTitle(self):
        self.browser.get('http://www.google.com')
        self.assertIn('Google', self.browser.title)

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
#
# browser = webdriver.Firefox()
#
# browser.get('http://www.yahoo.com')
# assert 'Yahoo' in browser.title
#
# elem = browser.find_element_by_name('p')  # Find the search box
# elem.send_keys('seleniumhq' + Keys.RETURN)
#
# browser.quit()


# class EdgeTestCase(unittest.TestCase):
#
#     def setUp(self):
#         self.browser = webdriver.Edge()
#         self.addCleanup(self.browser.quit)
#
#     def testPageTitle(self):
#         self.browser.get('http://www.google.com')
#         self.assertIn('Google', self.browser.title)


if __name__ == '__main__':
    unittest.main(verbosity=2)


