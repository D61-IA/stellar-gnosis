import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from catalog.models import CommentFlag, Comment, Paper
from catalog.forms import FlaggedCommentForm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GoogleTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Chrome()
        # login
        cls.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/1/')
        username = cls.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys('Gregg')

        pwd = cls.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys('testpassword')

        cls.browser.find_element_by_tag_name('form').submit()

        cls.paper = Paper.objects.get(pk=1)
        cls.comments = cls.paper.comment_set
        cls.sorted_comments = cls.comments.order_by('-created_at')
        cls.comment_container = cls.browser.find_element_by_css_selector('ul.list-group')
        cls.comment_items = cls.comment_container.find_elements_by_css_selector('li.list-group-item')
        for item in cls.comment_items:
            tmp = item.find_elements_by_class_name('open_flag_dialog')
            flagged = item.find_elements_by_class_name('flagged')
            if len(tmp) > 0 and len(flagged) == 0:
                cls.first_comment = item
                break

# the following tests are designed to test on comments that are yet flagged, make sure the page has such comments.
    # assert each comment has the correct flag status shown on the flag UI
    def testFlagUIs(self):
        for i in range(len(self.comment_items)):
            rst = len(self.comment_items[i].find_elements_by_class_name('flagged')) > 0
            b = self.sorted_comments[i].is_flagged

            self.assertEqual(rst, b)

    # assert pop up flag form is unhidden when flag icon is clicked
    def testFlagClick(self):
        first_comment = self.first_comment
        if first_comment is not None:
            flag_clickable = first_comment.find_element_by_class_name('open_flag_dialog')
            flag_clickable.click()

            a1 = self.browser.find_element_by_id('flag_form_container').get_attribute('hidden')
            self.assertEqual(a1, None)
        else:
            print("No comments from other users available on the paper.")

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
        if labels is not None:
            for i in range(len(labels)):
                self.assertEqual(true_labels[i], labels[i].text)
        else:
            print("Form radio buttons not found.")

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
        if self.first_comment is not None:
            first_comment = self.first_comment
            arr = first_comment.find_elements_by_class_name("flagged")
            self.assertEqual(len(arr), 1)

            arr = first_comment.find_elements_by_class_name("material-icons")
            self.assertEqual(arr[0].text, "flag")


class FirefoxTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        # login
        cls.browser.get('http://127.0.0.1:8000/accounts/login/?next=/catalog/paper/1/')
        username = cls.browser.find_element_by_id('id_login')
        username.clear()
        username.send_keys('Gregg')

        pwd = cls.browser.find_element_by_id('id_password')
        pwd.clear()
        pwd.send_keys('testpassword')

        cls.browser.find_element_by_tag_name('form').submit()

        cls.paper = Paper.objects.get(pk=1)
        cls.comments = cls.paper.comment_set
        cls.sorted_comments = cls.comments.order_by('-created_at')

        # wait for Ajax response
        wait = WebDriverWait(cls.browser, 10)
        element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list-group')))

        cls.comment_container = cls.browser.find_element_by_css_selector('ul.list-group')
        cls.comment_items = cls.comment_container.find_elements_by_css_selector('li.list-group-item')
        for item in cls.comment_items:
            tmp = item.find_elements_by_class_name('open_flag_dialog')
            flagged = item.find_elements_by_class_name('flagged')
            if len(tmp) > 0 and len(flagged) == 0:
                cls.first_comment = item
                break

    # the following tests are designed to test on comments that are yet flagged, make sure the page has such comments.
    # assert each comment has the correct flag status shown on the flag UI
    def testFlagUIs(self):
        for i in range(len(self.comment_items)):
            rst = len(self.comment_items[i].find_elements_by_class_name('flagged')) > 0
            b = self.sorted_comments[i].is_flagged

            self.assertEqual(rst, b)

    # assert pop up flag form is unhidden when flag icon is clicked
    def testFlagClick(self):
        first_comment = self.first_comment
        if first_comment is not None:
            flag_clickable = first_comment.find_element_by_class_name('open_flag_dialog')
            flag_clickable.click()

            a1 = self.browser.find_element_by_id('flag_form_container').get_attribute('hidden')
            self.assertEqual(a1, None)
        else:
            print("No comments from other users available on the paper.")

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
        if labels is not None:
            for i in range(len(labels)):
                self.assertEqual(true_labels[i], labels[i].text)
        else:
            print("Form radio buttons not found.")

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
        if self.first_comment is not None:
            first_comment = self.first_comment
            arr = first_comment.find_elements_by_class_name("flagged")
            self.assertEqual(len(arr), 1)

            arr = first_comment.find_elements_by_class_name("material-icons")
            self.assertEqual(arr[0].text, "flag")



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


