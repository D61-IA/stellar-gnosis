from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from catalog.models import Paper, Person, Dataset, Venue, Comment, Code
from catalog.models import ReadingGroup, ReadingGroupEntry
from catalog.models import Collection, CollectionEntry
from urllib.request import urlopen, Request
from catalog.forms import (
    PaperForm,
    DatasetForm,
    VenueForm,
    CommentForm,
    PaperImportForm,
)
from catalog.forms import (
    SearchVenuesForm,
    SearchPapersForm,
    SearchPeopleForm,
    SearchDatasetsForm,
    SearchCodesForm,
    PaperConnectionForm,
)
from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db
from datetime import date
from nltk.corpus import stopwords
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from django.contrib import messages
from catalog.views.views_codes import _code_find
import re



def analysis_url(url) :
    # check if a particular url starts with http , it is important as JMLR does not support https
    source_website = "false"
    if url.startswith("http://"):
        url = url[7:]
    # check if url includes https, and if not add it
    if not url.startswith("https://"):
        url = "https://" + url
    # check whether the url is from a supported website
    # from arXiv.org
    if url.startswith("https://arxiv.org"):
        source_website = "arxiv"
        print("source from arXiv")
    # from NeurlIPS
    elif url.startswith("https://papers.nips.cc/paper"):
        source_website = "nips"
        print("source from nips")
    # for urls of JMLR, they do not support https , so we need to change it to http instead
    elif url.startswith("https://www.jmlr.org/papers"):
        url = "http://" + url[8:]
        source_website = "jmlr"
        print("source from jmlr")
    elif url.startswith("https://proceedings.mlr.press/v") and url.endswith(".html"):
        url = "http://" + url[8:]
        source_website = "pmlr"
        print("source from pmlr")
    # from IEEE
    elif url.startswith("https://ieeexplore.ieee.org/document/") \
            or url.startswith("https://ieeexplore.ieee.org/abstract/document/"):
        source_website = "ieee"
        print("source from ieee")
    # from ACM
    elif url.startswith("https://dl.acm.org/"):
        source_website = "acm"
        print("source from acm")
    validity = True if (source_website != "false") else False
    return validity, source_website, url


def check_valid_paper_type_ieee(bs4obj):
    text = bs4obj.get_text()
    # the paper type is stored in a format of "xploreDocumentType":"paper_type"
    i = text.find('''"xploreDocumentType":"''')
    start = i + 22
    i = start
    count = 1
    while count != 0:
        if text[i] == '''"''':
            count = 0
        i += 1
    paper_type = text[start:i - 1]
    print(paper_type)
    if paper_type == "Journals & Magazine":
        return True
    return False


# this function is used to find the abstract for a paper from IEEE
def get_abstract_from_IEEE(bs4obj):
    """
        Extract paper abstract from the source website.
        :param bs4obj:
        :return: abstract
    """
    text = bs4obj.get_text()
    i = text.find('''"abstract":"''')
    start = None
    count = 0
    abstract = None
    if text[i + 12:i + 16] == "true":
        i = text.find('''"abstract":"''', i + 16)
        start = i + 12
        i = start
        count = 1
    while count != 0:
        if text[i] == '''"''':
            if text[i + 1] == "," and text[i + 2] == '''"''':
                count = 0
        i += 1
        abstract = text[start:i]
    return abstract


# this function is used to find the abstract for a paper from ACM
def get_abstract_from_ACM(bs4obj):
    """
        Extract paper abstract from the source website.
        :param bs4obj:
        :return: abstract
    """
    abstract = bs4obj.find("div", {"style": "display:inline"})
    if abstract:
        abstract = abstract.get_text()
    else:
        abstract = bs4obj.find("meta", {"name": "citation_abstract_html_url"})
        abstract_url = str(abstract)
        start = abstract_url.find('"')
        end = abstract_url.find('"', start + 1)
        abstract_url = abstract_url[start + 1:end]
        if abstract_url == "Non":
            return None
        abstract_url += "&preflayout=flat"
        headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
        req = Request(abstract_url, headers=headers)
        html = urlopen(req)
        bs4obj1 = BeautifulSoup(html,features="html.parser")
        abstract = bs4obj1.findAll("div", {"style": "display:inline"})
        abstract = abstract[0]
        if abstract:
            abstract = abstract.get_text()
    return abstract

def get_abstract_from_jmlr(bs4obj):
    abstract = bs4obj.find("p", {"class": "abstract"})
    if abstract is not None:
        abstract = abstract.get_text()
    else:
        # for some papers from JMLR , the abstract is stored without a tag,so this will find the abstract
        abstract = bs4obj.find("h3")
        if abstract is not None:
            abstract = abstract.next_sibling
        if abstract.strip() is "":
            abstract = abstract.next_sibling.text
    return abstract

def get_authors_from_arxiv(bs4obj):
    authorList = bs4obj.findAll("div", {"class": "authors"})
    if authorList:
        if len(authorList) > 1:
            # there should be just one but let's just take the first one
            authorList = authorList[0]
        # for author in authorList:
        #     print("type of author {}".format(type(author)))
        author_str = authorList[0].get_text()
        if author_str.startswith("Authors:"):
            author_str = author_str[8:]
        return author_str
    else :
        return None

def get_authors_from_nips(bs4obj):
    # authors are found to be list objects , so needs to join them to get the author string
    authorList = bs4obj.findAll("li", {"class": "author"})
    if authorList:
        authorList = [author.text for author in authorList]
        author_str = ','.join(authorList)
        return author_str
    else :
        return None

def get_authors_from_jmlr(bs4obj):
    # in JMLR authors are found in the html tag "i"
    authorList = bs4obj.findAll("i")
    if authorList:
        if len(authorList) >= 1:
            author_str = authorList[0].text
            return author_str
    else :
        return None

def get_authors_from_pmlr(bs4obj):
    authorlist = bs4obj.find("div", {"id":"authors"}).get_text()
    if authorlist:
        authorlist = authorlist.replace('\r', '').replace('\n', '').replace(';','')
        authorlist = [x.strip() for x in authorlist.split(',')]
        author_str = ','.join(authorlist)
        return author_str
    else :
        return None

# the two functions below are used to abstract author names from IEEE
# to abstract the author name from a format of "name":"author_name"
def find_author_from_IEEE_author_info(text):
    i = text.find('''"name":''')
    start = i + 8
    i = i + 8
    while text[i] != '''"''':
        i = i + 1
    author = text[start:i]
    return author

# to find the author names as a list
def find_author_list_from_IEEE(bs4obj):
    text = bs4obj.get_text()
    # to find the string which stores information of authors, which is stored in a
    # format of "authors":[{author 1 info},{author 2 info}]
    i = text.find('''"authors":[''')
    if i == -1:
        return []
    while text[i] != '[':
        i = i + 1
    i = i + 1
    array_count = 1
    bracket_count = 0
    bracket_start = 0
    author_list = []
    while array_count != 0:
        if text[i] == '{':
            if bracket_count == 0:
                bracket_start = i
            bracket_count = bracket_count + 1
        if text[i] == '}':
            bracket_count = bracket_count - 1
            if bracket_count == 0:
                author_list.append(find_author_from_IEEE_author_info(text[bracket_start:i]))
        if text[i] == ']':
            array_count = array_count - 1
        if text[i] == '[':
            array_count = array_count + 1
        i = i + 1
    return author_list

def get_authors_from_IEEE(bs4obj):
    authorList = find_author_list_from_IEEE(bs4obj)
    if authorList:
        authorList = [author for author in authorList]
        author_str = ','.join(authorList)
        return author_str
    else:
        return None

def get_authors_from_ACM(bs4obj):
    author_str = bs4obj.find("meta", {"name": "citation_authors"})
    author_str = str(author_str)
    # print("get_authors() downloaded author_str: {}".format(author_str))
    start = author_str.find('"')
    end = author_str.find('"', start + 1)
    author_str = author_str[start + 1:end]

    author_str_rev = ""
    for n in author_str.split(";"):
        if len(author_str_rev) == 0:
            author_str_rev = ", ".join(n.split(",")[::-1])
        else:
            author_str_rev = author_str_rev + "; " + ",".join(n.split(", ")[::-1])
    #print("get_authors() author_str_rev: {}".format(author_str_rev))
    author_str = author_str_rev.replace(",", "")
    author_str = author_str.replace("; ", ",")
    #print("get_authors() cleaned author_str: {}".format(author_str))
    # names are last, first so reverse to first, last
    return author_str

def get_ddl_from_IEEE(bs4obj):
    text = bs4obj.get_text()
    # the ddl link is stored in a format of "pdfUrl":"download_link"
    i = text.find('''"pdfUrl":"''')
    start = i + 10
    i = start
    count = 1
    while count != 0:
        if text[i] == '''"''':
            count = 0
        i += 1
    ddl = text[start:i - 1]
    ddl = "https://ieeexplore.ieee.org" + ddl
    return ddl
