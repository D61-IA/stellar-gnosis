from django.test import TestCase
from django.contrib.auth.models import User
from catalog.views.views import(
    _find_paper,
    paper_create_from_url,
)
from neomodel.exceptions import RequiredProperty
from django.http import HttpRequest


# Create your tests here.
# To run this test, use command: py -3 manage.py test tests.test_paper_import
class PaperImport(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='gnosis', email='gnosis@gnosis.com', password='gnosis')

    def test_import_content(self):
        """ For this test, a neo4j database must be running """
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        request.session = {}

        # test for arxiv url
        request.POST["url"] = "https://arxiv.org/abs/1607.00653"
        re = paper_create_from_url(request)
        self.assertTrue('location' in re._headers)      # check if it redirects to the paper create page

        # test whether specific entries are accurate
        self.assertEquals(request.session["from_external"], True)
        self.assertEquals(request.session["external_title"], "node2vec: Scalable Feature Learning for Networks")
        self.assertEquals(request.session["external_abstract"][:10], "Prediction")
        self.assertEquals(request.session["external_abstract"][-9:], "networks.")
        self.assertEquals(request.session["external_url"], "https://arxiv.org/abs/1607.00653")
        self.assertEquals(request.session["external_authors"], "Aditya Grover, Jure Leskovec")

        # test for NeurIPS url
        request.POST["url"] = "papers.nips.cc/paper/7286-efficient-algorithms-for-" \
                              "non-convex-isotonic-regression-through-submodular-optimization"

        re = paper_create_from_url(request)
        self.assertTrue('location' in re._headers)     # check if it redirects to the paper create page

        # test whether specific entries are accurate
        self.assertEquals(request.session["from_external"], True)
        self.assertEquals(request.session["external_title"],
                          "Efficient Algorithms for Non-convex Isotonic Regression through Submodular Optimization")
        self.assertEquals(request.session["external_abstract"][:2], "We")
        self.assertEquals(request.session["external_abstract"][-5:], "time.")
        self.assertEquals(request.session["external_url"],
                          "https://papers.nips.cc/paper/7286-efficient-algorithms-for-non-convex"
                          "-isotonic-regression-through-submodular-optimization")  # if https"// is added automatically
        self.assertEquals(request.session["external_authors"], "Francis Bach")

        # test for JMLR url
        request.POST["url"] = "http://www.jmlr.org/papers/v20/15-192.html"

        re = paper_create_from_url(request)
        self.assertTrue('location' in re._headers)  # check if it redirects to the paper create page

        # test whether specific entries are accurate
        self.assertEquals(request.session["from_external"], True)
        self.assertEquals(request.session["external_title"],
                          " Adaptation Based on Generalized Discrepancy ")
        self.assertTrue(request.session["external_abstract"].startswith("We"))
        self.assertEquals(request.session["external_abstract"][-13:], "minimization.")
        self.assertEquals(request.session["external_url"],
                          "http://www.jmlr.org/papers/v20/15-192.html")
        self.assertEquals(request.session["external_authors"], "Corinna Cortes, Mehryar Mohri, Andrés Muñoz Medina")

    def test_import_invalid_urls(self):
        """ For this test, a neo4j database must be running """
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        request.session = {}

        # test unsupported url
        url = "www.google.com"
        request.POST["url"] = url
        re = paper_create_from_url(request)
        # check that it does not redirect to the paper create page
        self.assertFalse('location' in re._headers)

        # test supported but invalid urls, i.e. content cannot be extracted
        invalid_urls = [
            "https://arxiv.org",                        # homepage of arxiv
            "https://arxiv.org/archive/astro-ph",     # topic selection page
            "https://arxiv.org/year/astro-ph/10",     # year selection page
            "https://arxiv.org/list/astro-ph/1001",   # selected results page(list of papers)
            # NeurIPS urls
            "https://papers.nips.cc/book/advances-in-neural-information-processing-systems-13-2000",  # all papers of 2010
            "https://papers.nips.cc/",                  # all papers
            # JMLR urls
            "http://www.jmlr.org/",                     # homepage of JMLR
            "http://www.jmlr.org/author-info.html",   # author info
            "http://www.jmlr.org/papers/",             # paper selection
            "http://www.jmlr.org/papers/v13/",        # volume selection
            # PMLR urls
            "http://proceedings.mlr.press/",  # homepage of pmlr
            "http://proceedings.mlr.press/v77/" , # volume page
            "http://proceedings.mlr.press/faq.html", # faq page

            # IEEE urls
            "https://www.ieee.org/",                               # homepage of IEEE
            "https://www.ieee.org/membership/join/index.html",  # member page
            "https://www.ieee.org/about/ieee-strategic-plan.html",  # strategy and plan page
            "https://www.ieee.org/publications/index.html",     # publication page
            "https://ieeexplore.ieee.org/author/37286693000",   # author page
            "https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=6488907", # journal
            "https://ieeexplore.ieee.org/search/searchresult.jsp?contentType=books&newsearch=true&queryText=smart", # search result page
            "https://ieeexplore.ieee.org/document/6813242",     # book**
            "https://ieeexplore.ieee.org/document/287238",      # proceeding**
            # ACM urls
            "https://dl.acm.org/citation.cfm?id=3281649",  # book
            "https://dl.acm.org/citation.cfm?id=3304087",  # book
            "https://dl.acm.org/citation.cfm?id=2841316",  # book
            "https://dl.acm.org/pubs.cfm",              # selection page for journals
            "https://dl.acm.org/pub.cfm?id=J401",       # journals
            "https://dl.acm.org/pub.cfm?id=J1191" ,     # journals
            "https://dl.acm.org/pub.cfm?id=J1268" ,     # magazine
            "https://dl.acm.org/mags.cfm",              # magazine selction page1
            "https://dl.acm.org/event.cfm?id=RE300",    # event page
            "https://dl.acm.org/books.cfm",             # book selection page
            "https://dl.acm.org/sig.cfm?id=SP1280",     # sepeical event
            "https://dl.acm.org/citation.cfm?id=2345396" ,  # proceeding
            "https://dl.acm.org/citation.cfm?id=1996010" ,  # proceeding
            # cvf urls
            "http://openaccess.thecvf.com/ICCV2017.py", # paper list
            "http://openaccess.thecvf.com/menu.py", # conference List
            "http://openaccess.thecvf.com/CVPR2019_workshops/menu.py", # workshop list
            # spg urls
            "https://link.springer.com/chapter/10.1007/978-981-13-5790-9_10", # charpter from a boook
            "https://link.springer.com/book/10.1007/978-3-030-11009-3", #conference proceedings
            # robotics proceedings
            "http://www.roboticsproceedings.org/rss14/authors.html", #author list
            "http://www.roboticsproceedings.org/rss13/index.html", #content list
            ]
        for url in invalid_urls:
            request.POST["url"] = url
            re = paper_create_from_url(request)
            # check that it does not redirect to the paper create page
            self.assertFalse('location' in re._headers)

    def test_import_valid_urls(self):
        """ For this test, a neo4j database must be running """
        request = HttpRequest()
        request.user = self.user
        request.method = 'POST'
        request.session = {}
        valid_urls = [
            "https://arxiv.org/abs/1904.06351",         # paper from 2019
            "https://arxiv.org/abs/1904.06352",
            "https://arxiv.org/abs/astro-ph/9204001",  # paper from 1992
            "https://arxiv.org/abs/astro-ph/9301001",
            "https://arxiv.org/abs/astro-ph/0001001",  # paper from 2000
            "https://arxiv.org/abs/1001.0005",          # paper from 2010
            # NIPS papers
            "https://papers.nips.cc/paper/7292-doubly-robust-bayesian-inference-for-non-stationary"
            "-streaming-data-with-beta-divergences",   # paper from 2018
            "https://papers.nips.cc/paper/4123-"       # paper from 2010
            "repeated-games-against-budgeted-adversaries",
            "https://papers.nips.cc/paper/1799-who-"   # paper from 2000
            "does-what-a-novel-algorithm-to-determine-function-localization",
            # JMLR papers
            "http://www.jmlr.org/papers/v13/zhang12a.html",   # paper from 2012
            "http://www.jmlr.org/papers/v11/strumbelj10a.html",  # paper from 2010
            "http://www.jmlr.org/papers/v1/meila00a.html",    # volume from 2000
            # PMLR papers
            "http://proceedings.mlr.press/v40/Kun15.html" ,   # paper from volume 40
            "http://proceedings.mlr.press/v78/thomason17a.html", # paper from volume 78
            "http://proceedings.mlr.press/v4/koehler08a.html" , # paper from volume 4
            # IEEE papers
            "https://ieeexplore.ieee.org/document/8290763",  # paper from 2018
            "https://ieeexplore.ieee.org/document/6681893",  # paper from 2013
            "https://ieeexplore.ieee.org/document/4501646",  # paper from 1965
            "https://ieeexplore.ieee.org/abstract/document/6472238",  # same as without abstract
            # ACM papers
            "https://dl.acm.org/citation.cfm?id=3239571",   # article
            "https://dl.acm.org/citation.cfm?id=2804405",   # article
            "https://dl.acm.org/citation.cfm?id=2907069",   # article
            # cvf papers
            "http://openaccess.thecvf.com/content_cvpr_2014/html/Liu_Weakly_Supervised_Multiclass_2014_CVPR_paper.html", #paper from CVPR 2014
            "http://openaccess.thecvf.com/content_ECCV_2018/html/Kaiyue_Pang_Deep_Factorised_Inverse-Sketching_ECCV_2018_paper.html", #paper from ECCV 2018
            "http://openaccess.thecvf.com/content_iccv_2013/html/Wang_Image_Co-segmentation_via_2013_ICCV_paper.html", # paper from ICCV 2013
            "http://openaccess.thecvf.com/content_CVPRW_2019/html/BIC/Laibacher_M2U-Net_Effective_and_Efficient_Retinal_Vessel_Segmentation_for_Real-World_Applications_CVPRW_2019_paper.html", # paper from workshops
            # springerLink papers
            "https://link.springer.com/article/10.1007/s10994-019-05799-x" , # Article
            "https://link.springer.com/chapter/10.1007/978-3-030-01246-5_11", # conference paper
            # robotics proceedings paper_source
            "http://www.roboticsproceedings.org/rss12/p02.html", # volume 12
            "http://www.roboticsproceedings.org/rss01/p10.html", # volume 1
            "http://www.roboticsproceedings.org/rss09/p01.html", # volume 9
            ]
        for url in valid_urls:
            request.POST["url"] = url
            paper_create_from_url(request)
            self.assertEquals(request.session["from_external"], True)
