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
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
        print("The server could not be found.")
    else:
        bs4obj = BeautifulSoup(html, features="html.parser")
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


def valid_jmlr_url(url):
    source_website = None
    if "jmlr.org" in url:
        source_website= "jmlr"
        if not url.startswith("http://"):
            url = "http://"+url
    return source_website, url


def analysis_url(url):
    """
    analysis whether a given url belongs to one of the supported website
    :param url
    :return: validity, source website name , and the input url
    """
    # check if a particular url starts with http , it is important as JMLR does not support https
    print(f"Received url {url}")
    source_website = "false"
    if url.startswith("http://"):
        url = url[7:]
    # check if url includes https, and if not add it
    if not url.startswith("https://"):
        url = "https://" + url

    print(f"Working url: {url}")
    # check whether the url is from a supported website
    # from arXiv.org
    if url.startswith("https://arxiv.org"):
        source_website = "arxiv"
        # print("source from arXiv")
    # from NeurlIPS
    elif url.startswith("https://papers.nips.cc/paper") or url.startswith("https://papers.neurips.cc/paper"):
        source_website = "nips"
        # print("source from nips")
    # for urls of JMLR, they do not support https , so we need to change it to http instead
    elif url.startswith("https://www.jmlr.org/papers") or url.startswith("https://jmlr.org/papers"):
        url = "http://" + url[8:]
        source_website = "jmlr"
        # print("source from jmlr")
    # from pmlr
    elif url.startswith("https://proceedings.mlr.press/v") and url.endswith(".html"):
        url = "http://" + url[8:]
        source_website = "pmlr"
        # print("source from pmlr")
    # from the cvf.com
    elif url.startswith("https://openaccess.thecvf.com/content_") and url.endswith(
        "paper.html"
    ):
        source_website = "cvf"
        # the cvf does not support https
        url = "http://" + url[8:]
        # print("source from cvf")
    # from the robotics proceedings http://roboticsproceedings.org/rss12/p01.html
    elif url.startswith("https://www.roboticsproceedings.org/rss") or url.startswith("https://roboticsproceedings.org/rss"):
        if not url.endswith("index.html") and not url.endswith("authors.html"):
            source_website = "rbtc"
            # print("source from roboticsproceedings")
            url = "http://" + url[8:]

    validity = True if (source_website != "false") else False
    return validity, source_website, url

def get_title(bs4obj, source_website):
    """
    Extract paper title from the source web.
    :param bs4obj:
    :return:
    """
    if source_website == "arxiv":
        titleList = bs4obj.findAll("h1", {"class": "title"})
    elif source_website == "nips":
        titleList = bs4obj.findAll("title")
    elif source_website == "jmlr":
        titleList = bs4obj.findAll("h2")
    elif source_website == "pmlr":
        title = bs4obj.find("title").get_text()
        return title
    elif source_website == "cvf":
        title = bs4obj.find("div", {"id": "papertitle"}).get_text()
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
    elif source_website == "nips":
        abstract = bs4obj.find("p", {"class": "abstract"})
        if abstract is not None:
            abstract = abstract.get_text()
    elif source_website == "jmlr":
        abstract = get_abstract_from_jmlr(bs4obj)
    elif source_website == "pmlr":
        abstract = bs4obj.find("div", {"id": "abstract"}).get_text().strip()
    elif source_website == "cvf":
        abstract = bs4obj.find("div", {"id": "abstract"}).get_text()
    elif source_website == "rbtc":
        abstract = get_abstract_from_rbtc(bs4obj)
    else:
        abstract = None
    # want to remove all the leading and ending white space and line breakers in the abstract
    if abstract is not None:
        abstract = abstract.strip()
        if source_website != "arxiv":
            abstract = abstract.replace("\r", "").replace("\n", "")
        else:
            abstract = abstract.replace("\n", " ")
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


def get_abstract_from_rbtc(bs4obj):
    abstract_para = bs4obj.findAll("p")[0]
    abstract_para_text = abstract_para.text
    abstract_index = abstract_para_text.find("Abstract:") + 9
    download_index = abstract_para_text.find("Download:")
    if abstract_para_text[abstract_index:download_index] == "":
        return abstract_para.next_sibling.text
    else:
        return abstract_para_text[abstract_index:download_index]


def get_authors(bs4obj, source_website):
    """
    Extract authors from the source website
    :param bs4obj, source_website；
    :return: None or a string with comma separated author names from first to last name
    """
    if source_website == "arxiv":
        return get_authors_from_arxiv(bs4obj)
    elif source_website == "nips":
        return get_authors_from_nips(bs4obj)
    elif source_website == "jmlr":
        return get_authors_from_jmlr(bs4obj)
    elif source_website == "pmlr":
        return get_authors_from_pmlr(bs4obj)
    elif source_website == "cvf":
        return get_authors_from_cvf(bs4obj)
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
    else:
        return None


def get_authors_from_nips(bs4obj):
    # authors are found to be list objects , so needs to join them to get the author string
    authorList = bs4obj.findAll("li", {"class": "author"})
    if authorList:
        authorList = [author.text for author in authorList]
        author_str = ",".join(authorList)
        return author_str
    else:
        return None


def get_authors_from_jmlr(bs4obj):
    # in JMLR authors are found in the html tag "i"
    authorList = bs4obj.findAll("i")
    if authorList:
        if len(authorList) >= 1:
            author_str = authorList[0].text
            return author_str.replace("(Corresponding author)", "")
    else:
        return None


def get_authors_from_pmlr(bs4obj):
    authorlist = bs4obj.find("div", {"id": "authors"}).get_text()
    if authorlist:
        authorlist = authorlist.replace("\r", "").replace("\n", "").replace(";", "")
        authorlist = [x.strip() for x in authorlist.split(",")]
        author_str = ",".join(authorlist)
        return author_str
    else:
        return None


def get_authors_from_cvf(bs4obj):
    author_str = bs4obj.find("div", {"id": "authors"}).find("b").get_text()
    return author_str

def get_authors_from_rbtc(bs4obj):
    authorList = bs4obj.findAll("i")
    if authorList:
        if len(authorList) >= 1:
            author_str = authorList[0].text
            return author_str
    else:
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
        download_link = url.replace("/abs/", "/pdf/", 1)
    elif source_website == "nips":
        download_link = url + ".pdf"
    elif source_website == "jmlr":
        download_link = bs4obj.find(href=re.compile("pdf"))["href"]
        if download_link.startswith("/papers/"):
            download_link = "http://www.jmlr.org" + download_link
    elif source_website == "pmlr":
        download_link = bs4obj.find("a", string="Download PDF")["href"]
    elif source_website == "cvf":
        download_link = url.replace("/html/", "/papers/", 1)
        download_link = download_link[:-4] + "pdf"
    elif source_website == "rbtc":
        download_link = url[:-4] + "pdf"
    else:
        download_link = None

    return download_link