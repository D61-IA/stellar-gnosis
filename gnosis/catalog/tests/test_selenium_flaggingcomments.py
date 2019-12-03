import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import CommentFlag, Comment, Paper
from catalog.forms import FlaggedCommentForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User


class ChromeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        # create temporary assets for testing
        cls.usrname = 'testuser118'
        cls.adminname = 'admin18'
        cls.email="testuser118@gnosis.stellargraph.io"

        cls.user = User.objects.create_user(username=cls.usrname, password="12345", email=cls.email)

        cls.admin = User.objects.create_superuser(username=cls.adminname,
                                                  password='abcdefg',
                                                  email="admin18@gnosis.stellargraph.io")

        cls.paper = Paper.objects.create(
            title="Best paper in the world",
            abstract="The nature of gravity.",
            download_link="https://google.com",
            created_by=cls.user,
        )

        cls.comment = Comment.objects.create(
            text="testing comment",
            created_by=cls.user,
            is_flagged=False,
            is_hidden=False,
            paper=cls.paper
        )

        # set testing browser to Chrome
        cls.browser = webdriver.Chrome()
        # login as admin
        cls.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/' + str(cls.paper.id) + '/')
        username = cls.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys(cls.adminname)

        pwd = cls.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys('abcdefg')

        cls.browser.find_element_by_tag_name('form').submit()

        cls.comment_container = cls.browser.find_element_by_css_selector('ul.list-group')
        # there should be only one comment in this fictional paper
        cls.first_comment = cls.comment_container.find_element_by_css_selector('li.list-group-item')

    # remove temporary assets from DB
    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

        cls.admin.delete()

        cls.paper.delete()

        cls.comment.delete()

        cls.browser.quit()

    # the following tests are designed to test on comments that are yet flagged, make sure the page has such comments.
    # assert each comment has the correct flag status shown on the flag UI
    def testFlagUIs(self):
        text = self.first_comment.find_element_by_class_name('material-icons').text
        self.assertEqual(text, 'outlined_flag')

    # assert pop up flag form is shown when flag icon is clicked
    def testFlagClick(self):
        first_comment = self.first_comment
        flag_clickable = first_comment.find_element_by_class_name('open_flag_dialog')
        flag_clickable.click()

        a1 = self.browser.find_element_by_id('flag_form_container').get_attribute('hidden')
        self.assertEqual(a1, None)

    def testFlagForm(self):
        flag_form = self.browser.find_element_by_id('flag_form')
        violations = flag_form.find_element_by_id('id_violation')
        labels = violations.find_elements_by_tag_name('label')
        form = FlaggedCommentForm()

        true_violations = form.fields['violation'].choices
        true_labels = []

        for v in true_violations:
            true_labels.append(v[0])

        # assert radio buttons have the right violations.
        for i in range(len(labels)):
            self.assertEqual(true_labels[i], labels[i].text)

        # assert the form has the right description field
        description = flag_form.find_elements_by_tag_name('textarea')
        self.assertEqual(len(description), 1)
        desc_id = description[0].get_attribute('id')
        self.assertEqual(desc_id, 'id_description')

    def testFlagValidFormSubmit(self):

        flag_form = self.browser.find_element_by_id('flag_form')

        # find first select option and select
        input_0 = flag_form.find_element_by_id('id_violation_0')
        input_0.click()

        # find description text area and insert text
        description = flag_form.find_element_by_id('id_description')
        description.clear()
        description.send_keys('violation description')

        flag_form.submit()

        # wait for Ajax response
        wait = WebDriverWait(self.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.ID, 'flag_response')))

        # after submit, assert flag form is hidden
        a1 = self.browser.find_element_by_id('flag_form_container').get_attribute('hidden')
        self.assertEqual(a1, 'true')

        # assert flag_response is unhidden after successful submit
        flag_response = self.browser.find_element_by_id('flag_response')
        self.assertEqual(flag_response.get_attribute('hidden'), None)

    def testFlaggedComment(self):
        first_comment = self.first_comment
        arr = first_comment.find_elements_by_class_name("flagged")
        self.assertEqual(len(arr), 1)

        arr = first_comment.find_elements_by_class_name("material-icons")
        self.assertEqual(arr[0].text, "flag")
        # self.browser.quit()

# class FirefoxTestCase(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#
#         # create temporary assets for testing
#         cls.usrname = 'testuser119'
#         cls.adminname = 'admin19'
#         cls.email = 'testuser119@gnosis.stellargraph.io'
#
#         cls.user = User.objects.create_user(username=cls.usrname, password="12345", email=cls.email)
#
#         cls.admin = User.objects.create_superuser(username=cls.adminname,
#                                                   password='abcdefg',
#                                                   email="admin19@gnosis.stellargraph.io")
#
#         cls.paper = Paper.objects.create(
#             title="Best paper in the world",
#             abstract="The nature of gravity.",
#             download_link="https://google.com",
#             created_by=cls.user,
#         )
#
#         cls.comment = Comment.objects.create(
#             text="testing comment",
#             created_by=cls.user,
#             is_flagged=False,
#             is_hidden=False,
#             paper=cls.paper
#         )
#
#         # set testing browser to Chrome
#         cls.browser = webdriver.Firefox()
#         # login as admin
#         cls.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/' + str(cls.paper.id) + '/')
#         username = cls.browser.find_element_by_id('id_login')
#         username.clear()
#         username.send_keys(cls.adminname)
#
#         pwd = cls.browser.find_element_by_id('id_password')
#         pwd.clear()
#         pwd.send_keys('abcdefg')
#
#         cls.browser.find_element_by_tag_name('form').submit()
#
#         # wait for Ajax response
#         wait = WebDriverWait(cls.browser, 10)
#         element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))
#
#         cls.comment_container = cls.browser.find_element_by_css_selector('ul.list-group')
#         # there should be only one comment in this fictional paper
#         cls.first_comment = cls.comment_container.find_element_by_css_selector('li.list-group-item')
#
#     # remove temporary assets from DB
#     @classmethod
#     def tearDownClass(cls):
#         cls.user.delete()
#
#         cls.admin.delete()
#
#         cls.paper.delete()
#
#         cls.comment.delete()
#
#     # the following tests are designed to test on comments that are yet flagged, make sure the page has such comments.
#     # assert each comment has the correct flag status shown on the flag UI
#     def testFlagUIs(self):
#         text = self.first_comment.find_element_by_class_name('material-icons').text
#         self.assertEqual(text, 'outlined_flag')
#
#     # assert pop up flag form is shown when flag icon is clicked
#     def testFlagClick(self):
#         first_comment = self.first_comment
#         flag_clickable = first_comment.find_element_by_class_name('open_flag_dialog')
#         flag_clickable.click()
#
#         a1 = self.browser.find_element_by_id('flag_form_container').get_attribute('hidden')
#         self.assertEqual(a1, None)
#
#     def testFlagForm(self):
#         flag_form = self.browser.find_element_by_id('flag_form')
#         violations = flag_form.find_element_by_id('id_violation')
#         labels = violations.find_elements_by_tag_name('label')
#
#         true_violations = FlaggedCommentForm().fields['violation'].choices
#         true_labels = [v[0] for v in true_violations]
#
#         # for v in true_violations:
#         #     true_labels.append(v[0])
#
#         # assert radio buttons have the right violations.
#         if labels is not None:
#             for i in range(len(labels)):
#                 self.assertEqual(true_labels[i], labels[i].text)
#         else:
#             print("Form radio buttons not found.")
#
#         # assert the form has the right description field
#         description = flag_form.find_elements_by_tag_name('textarea')
#         self.assertEqual(len(description), 1)
#         desc_id = description[0].get_attribute('id')
#         self.assertEqual(desc_id, 'id_description')
#
#     def testFlagValidFormSubmit(self):
#
#         flag_form = self.browser.find_element_by_id('flag_form')
#
#         # find first select option and select
#         input_0 = flag_form.find_element_by_id('id_violation_0')
#         input_0.click()
#
#         # find description text area and insert text
#         description = flag_form.find_element_by_id('id_description')
#         description.clear()
#         description.send_keys('violation description')
#
#         flag_form.submit()
#
#         # wait for Ajax response
#         wait = WebDriverWait(self.browser, 10)
#         element = wait.until(EC.visibility_of_element_located((By.ID, 'flag_response')))
#
#         # after submit, assert flag form is hidden
#         a1 = self.browser.find_element_by_id('flag_form_container').get_attribute('hidden')
#         self.assertEqual(a1, 'true')
#
#         # assert flag_response is unhidden after successful submit
#         flag_response = self.browser.find_element_by_id('flag_response')
#         self.assertEqual(flag_response.get_attribute('hidden'), None)
#
#     def testFlaggedComment(self):
#         first_comment = self.first_comment
#         arr = first_comment.find_elements_by_class_name("flagged")
#         self.assertEqual(len(arr), 1)
#
#         arr = first_comment.find_elements_by_class_name("material-icons")
#         self.assertEqual(arr[0].text, "flag")
#         self.browser.quit()



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
