from catalog.forms import PaperForm, PaperImportForm, PersonForm, DatasetForm, VenueForm, CommentForm, CodeForm, \
    SearchVenuesForm, SearchDatasetsForm, SearchPapersForm, SearchPeopleForm, SearchCodesForm, FlaggedCommentForm
from django.test import TestCase
import datetime as dt


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_form


#
# Search forms test
#
class SearchVenuesFormTest(TestCase):

    def test_fields(self):
        data = {'venue_name': "name",
                "venue_publication_year": "1995"}
        form = SearchVenuesForm(data)
        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")

    def test_clean_venue_name(self):
        data = {'venue_name': "name",
                "venue_publication_year": "1995"}
        form = SearchVenuesForm(data)
        if form.is_valid():
            x = form.clean_venue_name()
            self.assertEquals(x, "name")
            self.assertTrue(form.fields['venue_name'].label is None or form.fields['venue_name'].label == 'venue_name')

    def test_clean_venue_publication_year(self):
        data = {'venue_name': "name",
                "venue_publication_year": "1995"}
        form = SearchVenuesForm(data)
        if form.is_valid():
            x = form.clean_venue_publication_year()
            self.assertEquals(x, "1995")
            self.assertTrue(form.fields['venue_publication_year'].label is None or form.fields[
                'venue_publication_year'].label == 'venue_publication_year')


class SearchDatasetsFormTest(TestCase):

    def test_fields(self):
        form = SearchDatasetsForm()
        self.assertEquals(form.fields["name"].label, "Name")
        self.assertEquals(form.fields["keywords"].label, "Keyword (single keyword, e.g. network, computer vision)")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")

    def test_clean_name(self):
        data = {'name': "name",
                "keywords": "ML"}
        form = SearchDatasetsForm(data)
        if form.is_valid():
            x = form.clean_name()
            self.assertTrue(x == "name")
            self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'Name')

    def test_clean_keywords(self):
        data = {'name': "name",
                "keywords": "ML"}
        form = SearchDatasetsForm(data)
        if form.is_valid():
            x = form.clean_keywords()
            self.assertTrue(x == "ML")
            self.assertTrue(form.fields['keywords'].label is None or
                            form.fields['keywords'].label == 'Keyword (single keyword, e.g. network, computer vision)')


class SearchPapersFormTest(TestCase):
    def test_fields(self):
        form = SearchPapersForm()
        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")

    def test_clean_paper_title(self):
        data = {'paper_title': "ML"}
        form = SearchPapersForm(data)
        if form.is_valid():
            x = form.clean_paper_title()
            self.assertTrue(x == "ML")
            self.assertTrue(
                form.fields['paper_title'].label is None or form.fields['paper_title'].label == 'paper_title')


class SearchPeopleFormTest(TestCase):

    def test_fields(self):
        form = SearchPeopleForm()
        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")

    def test_clean_person_name(self):
        data = {"person_name": "Alice"}
        form = SearchPeopleForm(data)
        if form.is_valid():
            x = form.clean_person_name()
            self.assertTrue(x == "Alice")
            self.assertTrue(
                form.fields['person_name'].label is None or form.fields['person_name'].label == 'person_name')


class SearchCodesFormTest(TestCase):

    def test_fields(self):
        form = SearchCodesForm()
        self.assertEquals(form.fields["keywords"].label, "Keywords (e.g. GCN, network, computer vision)")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")

    def test_clean_keywords(self):
        data = {"keywords": "ML"}
        form = SearchCodesForm(data)
        if form.is_valid():
            x = form.clean_keywords()
            self.assertTrue(x == "ML")
            self.assertTrue(
                form.fields['keywords'].label is None
                or form.fields['keywords'].label == "Keywords (e.g. GCN, network, computer vision)")


#
# Model forms test
#

class PaperFormTest(TestCase):

    def test_fields(self):
        form = PaperForm()
        self.assertEquals(form.fields["title"].label, "Title*")
        self.assertEquals(form.fields["abstract"].label, "Abstract*")
        self.assertEquals(form.fields["keywords"].label, "Keywords")
        self.assertEquals(form.fields["download_link"].label, "Download Link*")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")

    def test_clean_title(self):
        data = {"title": "t", "abstract": "a", "keywords": "k", "download_link": "d"}
        form = PaperForm(data)
        if form.is_valid():
            x = form.clean_title()
            self.assertTrue(x == "t")
            self.assertTrue(form.fields['title'].label is None or form.fields['title'].label == 'Title*')

    def test_clean_abstract(self):
        data = {"title": "t", "abstract": "a", "keywords": "k", "download_link": "d"}
        form = PaperForm(data)
        if form.is_valid():
            x = form.clean_abstract()
            self.assertTrue(x == "a")
            self.assertTrue(form.fields['abstract'].label is None or form.fields['abstract'].label == 'Abstract*')

    def test_clean_keywords(self):
        data = {"title": "t", "abstract": "a", "keywords": "k", "download_link": "d"}
        form = PaperForm(data)
        if form.is_valid():
            x = form.clean_keywords()
            self.assertTrue(x == "k")
            self.assertTrue(form.fields['keywords'].label is None or form.fields['keywords'].label == 'Keywords')

    def test_clean_download_link(self):
        data = {"title": "t", "abstract": "a", "keywords": "k", "download_link": "d"}
        form = PaperForm(data)
        if form.is_valid():
            x = form.clean_download_link()
            self.assertTrue(x == "d")
            self.assertTrue(form.fields['download_link'].label is None
                            or form.fields['download_link'].label == 'Download Link*')


class PaperImportFormTest(TestCase):

    def test_clean_url(self):
        data = {"url": "www.google.com"}
        form = PaperImportForm(data)
        if form.is_valid():
            x = form.clean_url()
            self.assertTrue(x == "www.google.com")
            # self.assertTrue(form.fields['url'].label is None
            #                 or form.fields['url'].label == 'Source URL, e.g., https://arxiv.org/abs/1607.00653*'+
            #                                                ' <br /> Currently supported websites: arXiv.org, '+
            #                                                'papers.nips.cc, www.jmlr.org/papers <br /> for papers '+
            #                                                'from JMLR, please provide link of the abstract([abs]) '+
            #                                                'page ')


class PersonFormTest(TestCase):

    def test_fields(self):
        form = PersonForm()
        self.assertEquals(form.fields["first_name"].label, "First Name*")
        self.assertEquals(form.fields["middle_name"].label, "Middle Name")
        self.assertEquals(form.fields["last_name"].label, "Last Name*")
        self.assertEquals(form.fields["affiliation"].label, "Affiliation")
        self.assertEquals(form.fields["website"].label, "Website")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")
            self.assertEquals(visible.field.widget.attrs["style"], "width:25em")

    def test_clean_first_name(self):
        data = {"first_name": "f", "middle_name": "m", "last_name": "l", "affiliation": "a", "website": "w"}
        form = PersonForm(data)
        if form.is_valid():
            x = form.clean_first_name()
            self.assertTrue(x == "f")
            self.assertTrue(form.fields['first_name'].label is None or form.fields['first_name'].label == 'First Name*')

    def test_clean_middle_name(self):
        data = {"first_name": "f", "middle_name": "m", "last_name": "l", "affiliation": "a", "website": "w"}
        form = PersonForm(data)
        if form.is_valid():
            x = form.clean_middle_name()
            self.assertTrue(x == "m")
            self.assertTrue(form.fields['middle_name'].label is None
                            or form.fields['middle_name'].label == 'Middle Name')

    def test_clean_last_name(self):
        data = {"first_name": "f", "middle_name": "m", "last_name": "l", "affiliation": "a", "website": "w"}
        form = PersonForm(data)
        if form.is_valid():
            x = form.clean_last_name()
            self.assertTrue(x == "l")
            self.assertTrue(form.fields['last_name'].label is None or form.fields['last_name'].label == 'Last Name*')

    def test_clean_affiliation(self):
        data = {"first_name": "f", "middle_name": "m", "last_name": "l", "affiliation": "a", "website": "w"}
        form = PersonForm(data)
        if form.is_valid():
            x = form.clean_affiliation()
            self.assertTrue(x == "a")
            self.assertTrue(form.fields['affiliation'].label is None
                            or form.fields['affiliation'].label == 'Affiliation')

    def test_clean_website(self):
        data = {"first_name": "f", "middle_name": "m", "last_name": "l", "affiliation": "a", "website": "w"}
        form = PersonForm(data)
        if form.is_valid():
            x = form.clean_website()
            self.assertTrue(x == "w")
            self.assertTrue(form.fields['website'].label is None or form.fields['website'].label == 'Website')


class DatasetFormTest(TestCase):

    def test_fields(self):
        form = DatasetForm()
        self.assertEquals(form.fields["name"].label, "Name*")
        self.assertEquals(form.fields["keywords"].label, "Keywords*")
        self.assertEquals(form.fields["description"].label, "Description*")
        self.assertEquals(form.fields["source_type"].label, "Type*")
        self.assertEquals(form.fields["publication_date"].label, "Publication Date (yyyy-mm-dd)")
        self.assertEquals(form.fields["website"].label, "Website")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")
            self.assertEquals(visible.field.widget.attrs["style"], "width:25em")

    def test_clean_name(self):
        data = {
            "name": "n",
            "keywords": "k",
            "description": "d",
            "source_type": "N",
            "publication_date": "1999-09-09",
            "website": "w"}
        form = DatasetForm(data)
        if form.is_valid():
            x = form.clean_name()
            self.assertTrue(x == "n")
            self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'Name*')

    def test_clean_keywords(self):
        data = {
            "name": "n",
            "keywords": "k",
            "description": "d",
            "source_type": "N",
            "publication_date": "1999-09-09",
            "website": "w"}
        form = DatasetForm(data)
        if form.is_valid():
            x = form.clean_keywords()
            self.assertTrue(x == "k")
            self.assertTrue(form.fields['keywords'].label is None or form.fields['keywords'].label == 'Keywords*')

    def test_clean_description(self):
        data = {
            "name": "n",
            "keywords": "k",
            "description": "d",
            "source_type": "N",
            "publication_date": "1999-09-09",
            "website": "w"}
        form = DatasetForm(data)
        if form.is_valid():
            x = form.clean_description()
            self.assertTrue(x == "d")
            self.assertTrue(form.fields['description'].label is None
                            or form.fields['description'].label == 'Description*')

    def test_clean_source_type(self):
        data = {
            "name": "n",
            "keywords": "k",
            "description": "d",
            "source_type": "N",
            "publication_date": "1999-09-09",
            "website": "w"}
        form = DatasetForm(data)
        if form.is_valid():
            x = form.clean_source_type()
            self.assertTrue(x == "N")
            self.assertTrue(form.fields['source_type'].label is None or form.fields['source_type'].label == 'Type*')

    def test_clean_publication_date(self):
        data = {
            "name": "n",
            "keywords": "k",
            "description": "d",
            "source_type": "N",
            "publication_date": "1999-09-09",
            "website": "w"}
        form = DatasetForm(data)
        if form.is_valid():
            x = form.clean_publication_date()
            self.assertEquals(x, dt.date(1999, 9, 9))
            self.assertTrue(form.fields['publication_date'].label is None
                            or form.fields['publication_date'].label == 'Publication Date (yyyy-mm-dd)')

    def test_clean_website(self):
        data = {
            "name": "n",
            "keywords": "k",
            "description": "d",
            "source_type": "N",
            "publication_date": "1999-09-09",
            "website": "w"}
        form = DatasetForm(data)
        if form.is_valid():
            x = form.clean_website()
            self.assertTrue(x == "w")
            self.assertTrue(form.fields['website'].label is None or form.fields['website'].label == 'Website')


class VenueFormTest(TestCase):

    def test_fields(self):
        form = VenueForm()
        self.assertEquals(form.fields["name"].label, "Name*")
        self.assertEquals(form.fields["publisher"].label, "Publisher*")
        self.assertEquals(form.fields["publication_date"].label, "Publication Date (yyyy-mm-dd)*")
        self.assertEquals(form.fields["type"].label, "Type*")
        self.assertEquals(form.fields["peer_reviewed"].label, "Peer Reviewed*")
        self.assertEquals(form.fields["keywords"].label, "Keywords*")
        self.assertEquals(form.fields["website"].label, "Website")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")
            self.assertEquals(visible.field.widget.attrs["style"], "width:25em")

    def test_clean_name(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_name()
            self.assertTrue(x == "n")
            self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'Name*')

    def test_clean_publisher(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_publisher()
            self.assertTrue(x == "p1")
            self.assertTrue(form.fields['publisher'].label is None or form.fields['publisher'].label == 'Publisher*')

    def test_clean_publication_date(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_publication_date()
            self.assertEquals(x, dt.date(1999, 9, 9))
            self.assertTrue(form.fields['publication_date'].label is None
                            or form.fields['publication_date'].label == 'Publication Date (yyyy-mm-dd)*')

    def test_clean_type(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_type()
            self.assertTrue(x == "J")
            self.assertTrue(form.fields['type'].label is None or form.fields['type'].label == 'Type*')

    def test_clean_peer_reviewed(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_peer_reviewed()
            self.assertTrue(x == "Y")
            self.assertTrue(form.fields['peer_reviewed'].label is None
                            or form.fields['peer_reviewed'].label == 'Peer Reviewed*')

    def test_clean_keywords(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_keywords()
            self.assertTrue(x == "k")
            self.assertTrue(form.fields['keywords'].label is None or form.fields['keywords'].label == 'Keywords*')

    def test_clean_website(self):
        data = {
            "name": "n",
            "publisher": "p1",
            "publication_date": "1999-09-09",
            "type": "J",
            "peer_reviewed": "Y",
            "keywords": "k",
            "website": "w",
        }
        form = VenueForm(data)
        if form.is_valid():
            x = form.clean_website()
            self.assertTrue(x == "w")
            self.assertTrue(form.fields['website'].label is None or form.fields['website'].label == 'Website')


class CommentFormTest(TestCase):

    def test_fields(self):
        form = CommentForm()
        self.assertEquals(form.fields["text"].label, "")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")
            self.assertEquals(visible.field.widget.attrs["style"], "width:35em")

    def test_clean_text(self):
        # data = {"text": "t", "publication_date": "2018-04-17"}
        data = {"text": "t"}
        form = CommentForm(data)
        if form.is_valid():
            x = form.clean_text()
            self.assertTrue(x == "t")
            self.assertTrue(form.fields['text'].label is None or form.fields['text'].label == "")

    # def test_clean_publication_date(self):
    #     data = {"text": "t", "publication_date": "2018-04-17"}
    #     form = CommentForm(data)
    #     if form.is_valid():
    #         x = form.clean_publication_date()
    #         self.assertTrue(x == "2018-04-17")
    #         self.assertTrue(form.fields['publication_date'].label is None or form.fields['publication_date'].label == 'publication_date')


class CodeFormTest(TestCase):

    def test_fields(self):
        form = CodeForm()
        self.assertEquals(form.fields["website"].label, "Website*")
        self.assertEquals(form.fields["keywords"].label, "Keywords*")
        self.assertEquals(form.fields["description"].label, "Description*")

        for visible in form.visible_fields():
            self.assertEquals(visible.field.widget.attrs["class"], "form-control")
            self.assertEquals(visible.field.widget.attrs["style"], "width:25em")

    def test_clean_keywords(self):
        data = {
            "website": "w", "keywords": "k", "description": "d"
        }
        form = CodeForm(data)
        if form.is_valid():
            x = form.clean_keywords()
            self.assertTrue(x == "k")
            self.assertTrue(form.fields['keywords'].label is None or form.fields['keywords'].label == 'Keywords*')

    def test_clean_description(self):
        data = {
            "website": "w", "keywords": "k", "description": "d"
        }
        form = CodeForm(data)
        if form.is_valid():
            x = form.clean_description()
            self.assertTrue(x == "d")
            self.assertTrue(form.fields['description'].label is None
                            or form.fields['description'].label == 'Description*')

    def test_clean_website(self):
        data = {
            "website": "w", "keywords": "k", "description": "d"
        }
        form = CodeForm(data)
        if form.is_valid():
            x = form.clean_website()
            self.assertTrue(x == "w")
            self.assertTrue(form.fields['website'].label is None or form.fields['website'].label == 'Website*')


class FlagFormTest(TestCase):

    def test_fields(self):
        form = FlaggedCommentForm()
        self.assertEquals(form.fields["violation"].label, "Violation")
        self.assertEquals(form.fields["description"].label, "Description")

    def test_violation_exceed_length(self):
        data = {
            "violation": "Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "
            "(The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, comes from a line in section 1.10.32.",
            "description": "test description"
        }
        form = FlaggedCommentForm(data)
        self.assertFalse(form.is_valid())

    def test_violation_outside_choice_field(self):
        data = {
            "violation": "This is not a choice",
            "description": "test description"
        }
        form = FlaggedCommentForm(data)
        self.assertFalse(form.is_valid())

    def test_unfilled_required_description_field(self):
        data = {
            "violation": "Child abuse"
        }
        form = FlaggedCommentForm(data)
        self.assertFalse(form.is_valid())

    def test_unfilled_required_violation_field(self):
        data = {
            "description": "test description"
        }
        form = FlaggedCommentForm(data)
        self.assertFalse(form.is_valid())

    def test_clean_description(self):
        data = {
            "violation": "Child abuse",
            "description": "test description"
        }
        form = FlaggedCommentForm(data)
        if form.is_valid():
            d = form.clean_description()
            self.assertTrue(d == "test description")
            self.assertTrue(
                form.fields['description'].label is None or form.fields['description'].label == 'Description*')

    def test_clean_violation(self):
        data = {
            "violation": "Child abuse",
            "description": "test description"
        }
        form = FlaggedCommentForm(data)
        if form.is_valid():
            v = form.clean_violation()
            self.assertTrue(v == "Child abuse")
            self.assertTrue(
                form.fields['violation'].label is None or form.fields['violation'].label == 'Violation*')
