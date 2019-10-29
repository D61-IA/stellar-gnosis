from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import re

def get_paper_info(url, source_website):
    """
    Extract paper information, title, abstract, and authors, from source website
    paper page.
    :param url, source_website:
    :return: title, authors, abstract, download_link
    """
    try:
        # html = urlopen("http://pythonscraping.com/pages/page1.html")
        url_copy = url
        if source_website == "acm":
            headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
            url = Request(url, headers=headers)
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
        print("The server could not be found.")
    else:
        bs4obj = BeautifulSoup(html, features="html.parser")
        if source_website == "ieee":
            if check_valid_paper_type_ieee(bs4obj) == False:
                print("invalid paper type from IEEE")
                return None, None, None, None
        if source_website == "spg":
            if check_valid_paper_type_spg(bs4obj) == False:
                print("invalid paper type from springer")
                return None, None, None, None
        if source_website == "acm":
            url = ""
            if bs4obj.find("a", {"title": "Buy this Book"}) or bs4obj.find("a", {"ACM Magazines"}) \
                    or bs4obj.find_all("meta", {"name": "citation_conference_title"}):
                print("invalid paper type from acm")
                return None, None, None, None
        # Now, we can access individual element in the page
        authors = get_authors(bs4obj, source_website)
        title = get_title(bs4obj, source_website)
        abstract = get_abstract(bs4obj, source_website)
        download_link = ""
        if authors and title and abstract:
            download_link = get_download_link(bs4obj, source_website, url)
        if download_link == "Non":
            download_link = url_copy
        # venue = get_venue(bs4obj)
        return title, authors, abstract, download_link
    return None, None, None, None

def analysis_url(url) :
    """
    analysis whether a given url belongs to one of the supported website
    :param url
    :return: validity, source website name , and the input url
    """
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
    # from pmlr
    elif url.startswith("https://proceedings.mlr.press/v") and url.endswith(".html"):
        url = "http://" + url[8:]
        source_website = "pmlr"
        print("source from pmlr")
    # from IEEE
    elif url.startswith("https://ieeexplore.ieee.org/document/") or url.startswith("https://ieeexplore.ieee.org/abstract/document/"):
        source_website = "ieee"
        print("source from ieee")
    # from ACM
    elif url.startswith("https://dl.acm.org/"):
        source_website = "acm"
        print("source from acm")
    # from the cvf.com
    elif url.startswith("https://openaccess.thecvf.com/content_") and url.endswith("paper.html") :
        source_website = "cvf"
        # the cvf does not support https
        url = "http://" + url[8:]
        print("source from cvf")
    # from the springer.com
    elif url.startswith("https://link.springer.com/chapter/") or url.startswith("https://link.springer.com/article/"):
        source_website = "spg"
        print("source from spg")
    # from the robotics proceedings
    elif url.startswith("https://www.roboticsproceedings.org/rss"):
        if not url.endswith("index.html") and not url.endswith("authors.html"):
            source_website = "rbtc"
            print("source from roboticsproceedings")
            url = "http://" + url[8:]

    validity = True if (source_website != "false") else False
    return validity, source_website, url

def check_valid_paper_type_ieee(bs4obj):
    """
    checks whether an url on IEEE is the Journal & magazine type
    """
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

def check_valid_paper_type_spg(bs4obj):
    text = bs4obj.get_text()
    # the paper type is stored as "Event Category"
    i = text.find("'Event Category':")
    start = i + 18
    i = start
    count = 1
    while count != 0:
        if text[i] == '''"''':
            count = 0
        i += 1
    paper_type = text[start:i - 1]
    print(paper_type)
    if "Conference Paper" in paper_type or "Article" in paper_type:
        return True
    return False

def get_title(bs4obj, source_website):
    """
    Extract paper title from the source web.
    :param bs4obj:
    :return:
    """
    if source_website == "arxiv":
        titleList = bs4obj.findAll("h1", {"class": "title"})
    elif source_website == 'nips':
        titleList = bs4obj.findAll("title")
    elif source_website == "jmlr":
        titleList = bs4obj.findAll("h2")
    elif source_website == "pmlr":
        title = bs4obj.find("title").get_text()
        return title
    elif source_website == "ieee":
        title = bs4obj.find("title").get_text()
        i = title.find("- IEEE")
        if i != -1:
            title = title[0:i]
        return title
    elif source_website == "acm":
        titleList = bs4obj.find("meta", {"name": "citation_title"})
        title = str(titleList)
        start = title.find('"')
        end = title.find('"', start + 1)
        title = title[start + 1:end]
        if title == "Non":
            return None
        return title
    elif source_website == "cvf":
        title = bs4obj.find("div",{"id":"papertitle"}).get_text()
        return title
    elif source_website == "spg":
        title = bs4obj.find("title").get_text()
        title = title.replace(" | SpringerLink","")
        return title
    elif source_website == "rbtc":
        title = bs4obj.find("h3").get_text()
        return title
    else:
        titleList = []
    # check the validity of the abstracted titlelist
    if titleList:
        if len(titleList) == 0:
            return None
        else:
            if len(titleList) > 1:
                print("WARNING: Found more than one title. Returning the first one.")
            # return " ".join(titleList[0].get_text().split()[1:])
            title_text = titleList[0].get_text()
            if title_text.startswith("Title:"):
                return title_text[6:]
            else:
                return title_text
    return None

def get_abstract(bs4obj, source_website):
    """
    Extract paper abstract from the source website.
    :param bs4obj, source_website:
    :return:
    """
    if source_website == "arxiv":
        abstract = bs4obj.find("blockquote", {"class": "abstract"})
        if abstract is not None:
            abstract = " ".join(abstract.get_text().split(" ")[1:])
    elif source_website == 'nips':
        abstract = bs4obj.find("p", {"class": "abstract"})
        if abstract is not None:
            abstract = abstract.get_text()
    elif source_website == "jmlr":
        abstract = get_abstract_from_jmlr(bs4obj)
    elif source_website == "pmlr":
        abstract = bs4obj.find("div", {"id": "abstract"}).get_text().strip()
    elif source_website == "ieee":
        abstract = get_abstract_from_IEEE(bs4obj)
    elif source_website == "acm":
        abstract = get_abstract_from_ACM(bs4obj)
    elif source_website == "cvf":
        abstract = bs4obj.find("div",{"id":"abstract"}).get_text()
    elif source_website == "spg":
        abstract = get_abstract_from_spg(bs4obj)
    elif source_website == "rbtc":
        abstract = get_abstract_from_rbtc(bs4obj)
    else:
        abstract = None
    # want to remove all the leading and ending white space and line breakers in the abstract
    if abstract is not None:
        abstract = abstract.strip()
        if source_website != "arxiv":
            abstract = abstract.replace('\r', '').replace('\n', '')
        else:
            abstract = abstract.replace('\n', ' ')
    return abstract

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

def get_abstract_from_spg(bs4obj):
    h2_list = bs4obj.findAll("h2",{"class":"Heading"})
    for heading in h2_list:
        if heading.get_text() == "Abstract":
            return heading.next_sibling.get_text()


def get_abstract_from_rbtc(bs4obj):
    abstract_para = bs4obj.findAll("p")[0]
    abstract_para_text = abstract_para.text
    abstract_index = abstract_para_text.find("Abstract:") +9
    download_index = abstract_para_text.find("Download:")
    if abstract_para_text[abstract_index:download_index] == "":
        return abstract_para.next_sibling.text
    else :
        return abstract_para_text[abstract_index:download_index]

def get_authors(bs4obj, source_website):
    """
    Extract authors from the source website
    :param bs4obj, source_website；
    :return: None or a string with comma separated author names from first to last name
    """
    if source_website == "arxiv":
        return get_authors_from_arxiv(bs4obj)
    elif source_website == 'nips':
        return get_authors_from_nips(bs4obj)
    elif source_website == "jmlr":
        return get_authors_from_jmlr(bs4obj)
    elif source_website == "pmlr":
        return get_authors_from_pmlr(bs4obj)
    elif source_website == "ieee":
        return get_authors_from_IEEE(bs4obj)
    elif source_website == "acm":
        return get_authors_from_ACM(bs4obj)
    elif source_website == "cvf":
        return get_authors_from_cvf(bs4obj)
    elif source_website == "spg":
        return get_authors_from_spg(bs4obj)
    elif source_website == "rbtc":
        return get_authors_from_rbtc(bs4obj)
    # if source website is not supported or the autherlist is none , return none
    return None

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

def get_authors_from_cvf(bs4obj):
    author_str = bs4obj.find("div",{"id":"authors"}).find("b").get_text()
    return author_str

def get_authors_from_spg(bs4obj):
    authorList = bs4obj.findAll("span",{"class":"authors__name"})
    if authorList:
        authorList = [author.text for author in authorList]
        author_str = ','.join(authorList)
        return author_str
    else :
        return None

def get_authors_from_rbtc(bs4obj):
    authorList = bs4obj.findAll("i")
    if authorList:
        if len(authorList) >= 1:
            author_str = authorList[0].text
            return author_str
    else :
        return None

def get_download_link(bs4obj, source_website, url):
    """
    Extract download link from paper page1
    :param bs4obj:
    return: download link of paper
    """
    if url.endswith("/"):
        url = url[:-1]
    if source_website == "arxiv":
        download_link = url.replace("/abs/", "/pdf/", 1) + ".pdf"
    elif source_website == "nips":
        download_link = url + ".pdf"
    elif source_website == "jmlr":
        download_link = bs4obj.find(href=re.compile("pdf"))['href']
        if download_link.startswith("/papers/"):
            download_link = "http://www.jmlr.org" + download_link
    elif source_website == "pmlr":
        download_link = bs4obj.find("a", string="Download PDF")['href']
    elif source_website == "ieee":
        download_link = get_ddl_from_IEEE(bs4obj)
    elif source_website == "acm":
        download_link = bs4obj.find("meta", {"name": "citation_pdf_url"})
        download_link = str(download_link)
        start = download_link.find('"')
        end = download_link.find('"', start + 1)
        download_link = download_link[start + 1:end]
        return download_link
    elif source_website == "cvf":
        download_link = url.replace("/html/","/papers/",1)
        download_link = download_link[:-4]+"pdf"
    elif source_website == "spg":
        download_link = get_ddl_from_spg(url)
    elif source_website == "rbtc":
        download_link = url[:-4]+"pdf"

    else:
        download_link = None
    return download_link

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

def get_ddl_from_spg(url):
    if "springer.com/chapter/" in url :
        download_link = url.replace("springer.com/chapter/","springer.com/content/pdf/",1)
        download_link = download_link + ".pdf"
        return download_link
    elif "springer.com/article/" in url :
        download_link = url.replace("springer.com/article/","springer.com/content/pdf/",1)
        download_link = download_link + ".pdf"
        return download_link
    else :
        return None


def get_venue(bs4obj):
    """
    Extract publication venue from arXiv.org paper page.
    :param bs4obj:
    :return:
    """
    venue = bs4obj.find("td", {"class": "tablecell comments mathjax"})
    if venue is not None:
        venue = venue.get_text().split(";")[0]
    return venue
