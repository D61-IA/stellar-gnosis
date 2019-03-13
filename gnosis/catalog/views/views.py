from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from catalog.models import Paper, Person, Dataset, Venue, Comment
from catalog.forms import PaperForm, DatasetForm, VenueForm, CommentForm, PaperImportForm
from catalog.forms import SearchVenuesForm, SearchPapersForm, SearchPeopleForm, SearchDatasetsForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from neomodel import db
from datetime import date
from nltk.corpus import stopwords
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from django.contrib import messages


#
# Paper Views
#
def get_paper_authors(paper):
    query = "MATCH (:Paper {title: {paper_title}})<--(a:Person) RETURN a"
    results, meta = db.cypher_query(query, dict(paper_title=paper.title))
    if len(results) > 0:
        authors = [Person.inflate(row[0]) for row in results]
    else:
        authors = []
    # pdb.set_trace()
    authors = ['{}. {}'.format(author.first_name[0], author.last_name) for author in authors]

    return authors


def get_paper_venue(paper):
    query = "MATCH (:Paper {title: {paper_title}})--(v:Venue) RETURN v"
    results, meta = db.cypher_query(query, dict(paper_title=paper.title))
    if len(results) == 1:  # there should only be one venue associated with a paper
        venue = [Venue.inflate(row[0]) for row in results][0]
    else:
        venue = None
    # pdb.set_trace()
    if venue is not None:
        return '{}, {}'.format(venue.name, venue.publication_date)
    else:
        return ''


def papers(request):
    # Retrieve the papers ordered by newest addition to DB first.
    # limit to maximum 50 papers until we get pagination to work.
    # However, even with pagination, we are going to want to limit
    # the number of papers retrieved for speed, especially when the
    # the DB grows large.
    all_papers = Paper.nodes.order_by('-created')[:50]
    # Retrieve all comments about this paper.
    all_authors = [', '.join(get_paper_authors(paper)) for paper in all_papers]
    all_venues = [get_paper_venue(paper) for paper in all_papers]

    papers = list(zip(all_papers, all_authors, all_venues))

    return render(request,
                  'papers.html',
                  {'papers': papers,
                   'papers_only': all_papers,
                   'num_papers': len(Paper.nodes.all())})


def paper_authors(request, id):
    """Displays the list of authors associated with this paper"""
    paper = _get_paper_by_id(id)
    print("Retrieved paper with title {}".format(paper.title))

    query = "MATCH (p:Paper)<-[r]-(a:Person) WHERE ID(p)={id} RETURN a, ID(r)"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        authors = [Person.inflate(row[0]) for row in results]
        relationship_ids = [row[1] for row in results]
    else:
        authors = []
    print("paper author link ids {}".format(relationship_ids))
    print("Found {} authors for paper with id {}".format(len(authors), id))

    # for rid in relationship_ids:
    delete_urls = [reverse('paper_remove_author', kwargs={'id': id, 'rid': rid}) for rid in relationship_ids]
    print("author remove urls")
    print(delete_urls)

    authors = zip(authors, delete_urls)

    return render(request,
                  'paper_authors.html',
                  {'authors': authors,
                   'paper': paper, })


# should limit access to admin users only!!
@staff_member_required
def paper_remove_author(request, id, rid):
    print("Paper id {} and edge id {}".format(id, rid))

    # Cypher query to delete edge of type authors with id equal to rid
    query = "MATCH ()-[r:authors]-() WHERE ID(r)={id} DELETE r"
    results, meta = db.cypher_query(query, dict(id=rid))

    return HttpResponseRedirect(reverse("paper_authors", kwargs={'id': id}))


def _get_paper_by_id(id):
    # Retrieve the paper from the database
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    paper = None
    if len(results) > 0:
        all_papers = [Paper.inflate(row[0]) for row in results]
        paper = all_papers[0]
    return paper


def paper_detail(request, id):
    # Retrieve the paper from the database
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        all_papers = [Paper.inflate(row[0]) for row in results]
        paper = all_papers[0]
    else:  # go back to the paper index page
        return render(request, 'papers.html', {'papers': Paper.nodes.all(), 'num_papers': len(Paper.nodes.all())})

    # Retrieve the paper's authors
    authors = get_paper_authors(paper)
    # authors is a list of strings so just concatenate the strings.
    authors = ", ".join(authors)

    # Retrieve all comments about this paper.
    query = "MATCH (:Paper {title: {paper_title}})<--(c:Comment) RETURN c"
    results, meta = db.cypher_query(query, dict(paper_title=paper.title))
    if len(results) > 0:
        comments = [Comment.inflate(row[0]) for row in results]
        num_comments = len(comments)
    else:
        comments = []
        num_comments = 0

    # Retrieve venue where paper was published.
    query = "MATCH (:Paper {title: {paper_title}})-->(v:Venue) RETURN v"
    results, meta = db.cypher_query(query, dict(paper_title=paper.title))
    if len(results) > 0:
        venues = [Venue.inflate(row[0]) for row in results]
        venue = venues[0]
    else:
        venue = None

    request.session['last-viewed-paper'] = id

    ego_network_json = _get_node_ego_network(paper.id, paper.title)

    print("ego_network_json: {}".format(ego_network_json))
    return render(request,
                  'paper_detail.html',
                  {'paper': paper,
                   'venue': venue,
                   'authors': authors,
                   'comments': comments,
                   'num_comments': num_comments,
                   'ego_network': ego_network_json})


def _get_node_ego_network(id, paper_title):
    '''
    Returns a json formatted string of the nodes ego network
    :param id:
    :return:
    '''
    query = "MATCH (s:Paper {title: {paper_title}})-->(t:Paper) RETURN t"
    results, meta = db.cypher_query(query, dict(paper_title=paper_title))
    ego_json = ''
    if len(results) > 0:
        target_papers = [Paper.inflate(row[0]) for row in results]
        print("Paper cites {} other papers.".format(len(target_papers)))
        ego_json = "{{data : {{id: '{}', title: '{}', href: '{}' }} }}".format(id,
                                                                               paper_title,
                                                                               reverse('paper_detail',
                                                                                       kwargs={'id': id}))
        for tp in target_papers:
            ego_json += ", {{data : {{id: '{}', title: '{}', href: '{}' }} }}".format(tp.id,
                                                                                      tp.title,
                                                                                      reverse('paper_detail',
                                                                                              kwargs={'id': tp.id}))
        for tp in target_papers:
            ego_json += ",{{data: {{ id: '{}{}', label: '{}', source: {}, target: {} }}}}".format(id, tp.id, 'cites',
                                                                                                  id, tp.id)
    else:
        print("No cited papers found!")

    return '[' + ego_json + ']'


def paper_find(request):
    message = None
    if request.method == 'POST':
        form = SearchPapersForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            english_stopwords = stopwords.words('english')
            paper_title = form.cleaned_data['paper_title'].lower()
            paper_title_tokens = [w for w in paper_title.split(' ') if not w in english_stopwords]
            paper_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in paper_title_tokens) + '+.*'
            query = "MATCH (p:Paper) WHERE  p.title =~ { paper_query } RETURN p LIMIT 25"
            print("Cypher query string {}".format(query))
            results, meta = db.cypher_query(query, dict(paper_query=paper_query))
            if len(results) > 0:
                print("Found {} matching papers".format(len(results)))
                papers = [Paper.inflate(row[0]) for row in results]
                return render(request, 'paper_results.html', {'papers': papers})
            else:
                message = "No results found. Please try again!"

    elif request.method == 'GET':
        print("Received GET request")
        form = SearchPapersForm()

    return render(request, 'paper_find.html', {'form': form, 'message': message})


@login_required
def paper_connect_venue(request, id):
    if request.method == 'POST':
        form = SearchVenuesForm(request.POST)
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            english_stopwords = stopwords.words('english')
            venue_name = form.cleaned_data['venue_name'].lower()
            venue_publication_year = form.cleaned_data['venue_publication_year']
            # TO DO: should probably check that data is 4 digits...
            venue_name_tokens = [w for w in venue_name.split(' ') if not w in english_stopwords]
            venue_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in venue_name_tokens) + '+.*'
            query = "MATCH (v:Venue) WHERE v.publication_date =~ '" + venue_publication_year[0:4] + \
                    ".*' AND v.name =~ { venue_query } RETURN v"
            results, meta = db.cypher_query(query, dict(venue_publication_year=venue_publication_year[0:4],
                                                        venue_query=venue_query))
            if len(results) > 0:
                venues = [Venue.inflate(row[0]) for row in results]
                print("Found {} venues that match".format(len(venues)))
                for v in venues:
                    print("\t{}".format(v))

                if len(results) > 1:
                    # ask the user to select one of them
                    return render(request, 'paper_connect_venue.html', {'form': form,
                                                                        'venues': venues,
                                                                        'message': 'Found more than one matching venues. Please narrow your search'})
                else:
                    venue = venues[0]
                    print('Selected Venue: {}'.format(venue))

                # retrieve the paper
                query = "MATCH (a) WHERE ID(a)={id} RETURN a"
                results, meta = db.cypher_query(query, dict(id=id))
                if len(results) > 0:
                    all_papers = [Paper.inflate(row[0]) for row in results]
                    paper = all_papers[0]
                    print("Found paper: {}".format(paper.title))
                    # check if the paper is connect with a venue; if yes, the remove link to
                    # venue before adding link to the new venue
                    query = 'MATCH (p:Paper)-[r:was_published_at]->(v:Venue) where id(p)={id} return v'
                    results, meta = db.cypher_query(query, dict(id=id))
                    if len(results) > 0:
                        venues = [Venue.inflate(row[0]) for row in results]
                        for v in venues:
                            print("Disconnecting from: {}".format(v))
                            paper.was_published_at.disconnect(v)
                            paper.save()
                else:
                    print("Could not find paper!")
                    # should not get here since we started from the actual paper...but what if we do end up here?
                    pass  # Should raise an exception but for now just pass
                # we have a venue and a paper, so connect them.
                print("Citation link not found, adding it!")
                messages.add_message(request, messages.INFO, "Link to venue added!")
                paper.was_published_at.connect(venue)
                return redirect('paper_detail', id=paper.id)
            else:
                # render new Venue form with the searched name as
                message = 'No matching venues found'

    if request.method == 'GET':
        form = SearchVenuesForm()
        message = None

    return render(request, 'paper_connect_venue.html', {'form': form, 'venues': None, 'message': message})


@login_required
def paper_connect_author_selected(request, id, aid):

    query = "MATCH (p:Paper), (a:Person) WHERE ID(p)={id} AND ID(a)={aid} MERGE (a)-[r:authors]->(p) RETURN r"
    results, meta = db.cypher_query(query, dict(id=id, aid=aid))

    if len(results) > 0:
        messages.add_message(request, messages.INFO, "Linked with author.")
    else:
        messages.add_message(request, messages.INFO, "Link to author failed!")

    return HttpResponseRedirect(reverse("paper_detail", kwargs={'id': id}))

@login_required
def paper_connect_author(request, id):
    if request.method == 'POST':
        form = SearchPeopleForm(request.POST)
        if form.is_valid():
            # search the db for the person
            # if the person is found, then link with paper and go back to paper view
            # if not, ask the user to create a new person
            name = form.cleaned_data['person_name']
            people_found = _person_find(name)

            if people_found is not None:
                print("Found {} people that match".format(len(people_found)))
                for person in people_found:
                    print("\t{} {} {}".format(person.first_name, person.middle_name, person.last_name))

                if len(people_found) > 0:
                    # for rid in relationship_ids:
                    author_connect_urls = [reverse('paper_connect_author_selected', kwargs={'id': id, 'aid': person.id}) for person in people_found]
                    print("author remove urls")
                    print(author_connect_urls)

                    authors = zip(people_found, author_connect_urls)

                    # ask the user to select one of them
                    return render(request, 'paper_connect_author.html', {'form': form,
                                                                         'people': authors,
                                                                         'message': ''})
                # else:
                #     person = people_found[0]  # one person found
                #     print('Selected person: {} {} {}'.format(person.first_name, person.middle_name, person.last_name))
                #
                # # retrieve the paper
                # query = "MATCH (a) WHERE ID(a)={id} RETURN a"
                # results, meta = db.cypher_query(query, dict(id=id))
                # if len(results) > 0:
                #     all_papers = [Paper.inflate(row[0]) for row in results]
                #     paper = all_papers[0]
                #     print("Found paper: {}".format(paper.title))
                #     # check if the paper is connect with the author; if yes, then do nothing,
                #     # otherwise add the link between paper and author
                #     query = 'MATCH (p:Paper)<-[r:authors]-(a:Person) where id(p)={id} and id(a)={author_id} return p'
                #     results, meta = db.cypher_query(query, dict(id=paper.id, author_id=person.id))
                #     if len(results) == 0:
                #         # person is not linked with paper so add the edge
                #         person.authors.connect(paper)
                #         messages.add_message(request, messages.INFO, "Linked with author!")
                #     else:
                #         messages.add_message(request, messages.INFO, "Link to author already exists!")
                # else:
                #     print("Could not find paper!")
                #     # should not get here since we started from the actual paper...but what if we do end up here?
                #     pass  # Should raise an exception but for now just pass
                # return redirect('paper_detail', id=paper.id)
            else:
                message = 'No matching people found'

    if request.method == 'GET':
        form = SearchPeopleForm()
        message = None

    return render(request, 'paper_connect_author.html', {'form': form, 'people': None, 'message': message})


@login_required
def paper_connect_paper(request, id):
    """
    View function for connecting a paper with another paper.

    :param request:
    :param id:
    :return:
    """
    message = None
    if request.method == 'POST':
        form = SearchPapersForm(request.POST)
        if form.is_valid():
            # search the db for the person
            # if the person is found, then link with paper and go back to paper view
            # if not, ask the user to create a new person
            paper_title_query = form.cleaned_data['paper_title']
            papers_found = _find_paper(paper_title_query)

            if len(papers_found) > 0:  # found more than one matching papers
                print("Found {} papers that match".format(len(papers_found)))
                for paper in papers_found:
                    print("\t{}".format(paper.title))

                if len(papers_found) > 1:
                    return render(request, 'paper_connect_paper.html', {'form': form,
                                                                        'papers': papers_found,
                                                                        'message': 'Found more than one matching papers. Please narrow your search'})
                else:
                    paper_target = papers_found[0]  # one person found
                    print('Selected paper: {}'.format(paper.title))

                # retrieve the paper
                query = "MATCH (a) WHERE ID(a)={id} RETURN a"
                results, meta = db.cypher_query(query, dict(id=id))
                if len(results) > 0:
                    all_papers = [Paper.inflate(row[0]) for row in results]
                    paper_source = all_papers[0]  # since we search by id only one paper should have been returned.
                    print("Found paper: {}".format(paper_source.title))
                    # check if the papers are already connected with a cites link; if yes, then
                    # do nothing. Otherwise, add the link.
                    query = 'MATCH (q:Paper)<-[r:cites]-(p:Paper) where id(p)={source_id} and id(q)={target_id} return p'
                    results, meta = db.cypher_query(query, dict(source_id=paper_source.id, target_id=paper_target.id))
                    if len(results) == 0:
                        # papers are not linked so add the edge
                        print("Citation link not found, adding it!")
                        paper_source.cites.connect(paper_target)
                        messages.add_message(request, messages.INFO, "Citation Added!")
                    else:
                        print("Citation link found not adding it!")
                        messages.add_message(request, messages.INFO, "Citation Already Exists!")
                else:
                    print("Could not find paper!")
                    messages.add_message(request, messages.INFO, "Could not find paper!")
                return redirect('paper_detail', id=id)
            else:
                message = 'No matching papers found'

    if request.method == 'GET':
        form = SearchPapersForm()

    return render(request, 'paper_connect_paper.html', {'form': form, 'papers': None, 'message': message})


@login_required
def paper_connect_dataset(request, id):
    """
    View function for connecting a paper with a dataset.

    :param request:
    :param id:
    :return:
    """
    if request.method == 'POST':
        form = SearchDatasetsForm(request.POST)
        if form.is_valid():
            # search the db for the dataset
            # if the dataset is found, then link with paper and go back to paper view
            # if not, ask the user to create a new dataset
            dataset_query_name = form.cleaned_data['name']
            dataset_query_keywords = form.cleaned_data['keywords']
            datasets_found = _dataset_find(dataset_query_name, dataset_query_keywords)

            if len(datasets_found) > 0:  # found more than one matching dataset
                print("Found {} datasets that match".format(len(datasets_found)))
                for dataset in datasets_found:
                    print("\t{}".format(dataset.name))

                if len(datasets_found) > 1:
                    return render(request, 'paper_connect_dataset.html', {'form': form,
                                                                          'datasets': datasets_found,
                                                                          'message': 'Found more than one matching datasets. Please narrow your search'})
                else:
                    dataset_target = datasets_found[0]  # one person found
                    print('Selected dataset: {}'.format(dataset_target.name))

                # retrieve the paper
                query = "MATCH (a) WHERE ID(a)={id} RETURN a"
                results, meta = db.cypher_query(query, dict(id=id))
                if len(results) > 0:
                    all_papers = [Paper.inflate(row[0]) for row in results]
                    paper_source = all_papers[0]  # since we search by id only one paper should have been returned.
                    print("Found paper: {}".format(paper_source.title))
                    # check if the papers are already connected with a cites link; if yes, then
                    # do nothing. Otherwise, add the link.
                    query = 'MATCH (d:Dataset)<-[r:evaluates_on]-(p:Paper) where id(p)={id} and id(d)={dataset_id} return p'
                    results, meta = db.cypher_query(query, dict(id=id, dataset_id=dataset_target.id))
                    if len(results) == 0:
                        # dataset is not linked with paper so add the edge
                        paper_source.evaluates_on.connect(dataset_target)
                        messages.add_message(request, messages.INFO, "Link to dataset added!")
                    else:
                        messages.add_message(request, messages.INFO, "Link to dataset already exists!")
                else:
                    print("Could not find paper!")
                return redirect('paper_detail', id=id)

            else:
                message = 'No matching datasets found'

    if request.method == 'GET':
        form = SearchDatasetsForm()
        message = None

    return render(request, 'paper_connect_dataset.html', {'form': form, 'datasets': None, 'message': message})


@login_required
def paper_update(request, id):
    # retrieve paper by ID
    # https://github.com/neo4j-contrib/neomodel/issues/199
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        all_papers = [Paper.inflate(row[0]) for row in results]
        paper_inst = all_papers[0]
    else:
        paper_inst = Paper()

    # if this is POST request then process the Form data
    if request.method == 'POST':

        form = PaperForm(request.POST)
        if form.is_valid():
            paper_inst.title = form.cleaned_data['title']
            paper_inst.abstract = form.cleaned_data['abstract']
            paper_inst.keywords = form.cleaned_data['keywords']
            paper_inst.download_link = form.cleaned_data['download_link']
            paper_inst.save()

            return HttpResponseRedirect(reverse('papers_index'))
    # GET request
    else:
        query = "MATCH (a) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=id))
        if len(results) > 0:
            all_papers = [Paper.inflate(row[0]) for row in results]
            paper_inst = all_papers[0]
        else:
            paper_inst = Paper()
        # paper_inst = Paper()
        form = PaperForm(initial={'title': paper_inst.title,
                                  'abstract': paper_inst.abstract,
                                  'keywords': paper_inst.keywords,
                                  'download_link': paper_inst.download_link, })

    return render(request, 'paper_update.html', {'form': form, 'paper': paper_inst})


def _find_paper(query_string):
    """
    Helper method to query the DB for a paper based on its title.
    :param query_string: The query string, e.g., title of paper to search for
    :return: <list> List of papers that match the query or empty list if none match.
    """
    papers_found = []

    english_stopwords = stopwords.words('english')
    paper_title = query_string.lower()
    paper_title_tokens = [w for w in paper_title.split(' ') if not w in english_stopwords]
    paper_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in paper_title_tokens) + '+.*'
    query = "MATCH (p:Paper) WHERE  p.title =~ { paper_query } RETURN p LIMIT 25"
    print("Cypher query string {}".format(query))
    results, meta = db.cypher_query(query, dict(paper_query=paper_query))

    if len(results) > 0:
        papers_found = [Paper.inflate(row[0]) for row in results]

    return papers_found


def _add_author(author, paper=None):
    """
    Adds author to the DB if author does not already exist and links to paper
    as author if paper is not None
    :param author:
    :param paper:
    """
    link_with_paper = False
    p = None
    people_found = _person_find(author, exact_match=True)
    author_name = author.strip().split(' ')
    if people_found is None:  # not in DB
        print("Author {} not in DB".format(author))
        p = Person()
        p.first_name = author_name[0]
        if len(author_name) > 2:  # has middle name(s)
            p.middle_name = author_name[1:-1]
        else:
            p.middle_name = None
        p.last_name = author_name[-1]
        p.save()  # save to DB
        link_with_paper = True
    elif len(people_found) == 1:
        # Exactly one person found. Check if name is an exact match.
        p = people_found[0]
        # NOTE: The problem with this simple check is that if two people have
        # the same name then the wrong person will be linked to the paper.
        if p.first_name == author_name[0] and p.last_name == author_name[-1]:
            if len(author_name) > 2:
                if p.middle_name == author_name[1:-1]:
                    link_with_paper = True
            else:
                link_with_paper = True
    else:
        print("Person with similar but not exactly the same name is already in DB.")

    if link_with_paper and paper is not None:
        print("Adding authors link to paper {}".format(paper.title[:50]))
        # link author with paper
        p.authors.connect(paper)


@login_required
def paper_create(request):
    user = request.user
    print("In paper_create() view.")
    message = ''
    if request.method == 'POST':
        print("   POST")
        paper = Paper()
        paper.created_by = user.id
        form = PaperForm(instance=paper, data=request.POST)
        if form.is_valid():
            # Check if the paper already exists in DB
            matching_papers = _find_paper(form.cleaned_data['title'])
            if len(matching_papers) > 0:  # paper in DB already
                message = "Paper already exists in Gnosis!"
                return render(request, 'paper_results.html', {'papers': matching_papers, 'message': message})
            else:  # the paper is not in DB yet.
                form.save()  # store
                # Now, add the authors and link each author to the paper with an "authors"
                # type edge.
                if request.session.get('from_arxiv', False):
                    paper_authors = request.session['arxiv_authors']
                    for paper_author in paper_authors.split(','):
                        print("Adding author {}".format(paper_author))
                        _add_author(paper_author, paper)

                request.session['from_arxiv'] = False  # reset
                # go back to paper index page.
                # Should this redirect to the page of the new paper just added?
                return HttpResponseRedirect(reverse('papers_index'))
    else:  # GET
        print("   GET")
        # check if this is a redirect from paper_create_from_arxiv
        # if so, then pre-populate the form with the data from arXiv,
        # otherwise start with an empty form.
        if request.session.get('from_arxiv', False) is True:
            title = request.session['arxiv_title']
            abstract = request.session['arxiv_abstract']
            url = request.session['arxiv_url']

            form = PaperForm(initial={'title': title,
                                      'abstract': abstract,
                                      'download_link': url})
        else:
            form = PaperForm()

    return render(request, 'paper_form.html', {'form': form, 'message': message})


def get_authors(bs4obj):
    """
    Extract authors from arXiv.org paper page
    :param bs4obj:
    :return: None or a string with comma separated author names from first to last name
    """
    authorList = bs4obj.findAll("div", {"class": "authors"})
    if authorList is not None:
        if len(authorList) > 1:
            # there should be just one but let's just take the first one
            authorList = authorList[0]

        # for author in authorList:
        # print("type of author {}".format(type(author)))
        author_str = authorList[0].get_text()
        if author_str.startswith("Authors:"):
            author_str = author_str[8:]
        return author_str
    # authorList is None so return None
    return None


def get_title(bs4obj):
    """
    Extract paper title from arXiv.org paper page.
    :param bs4obj:
    :return:
    """
    titleList = bs4obj.findAll("h1", {"class": "title"})
    if titleList is not None:
        if len(titleList) == 0:
            return None
        else:
            if len(titleList) > 1:
                print("WARNING: Found more than one title. Returning the first one.")
            # return " ".join(titleList[0].get_text().split()[1:])
            title_text = titleList[0].get_text()
            if title_text.startswith('Title:'):
                return title_text[6:]
            else:
                return title_text
    return None


def get_abstract(bs4obj):
    """
    Extract paper abstract from arXiv.org paper page.
    :param bs4obj:
    :return:
    """
    abstract = bs4obj.find("blockquote", {"class": "abstract"})
    if abstract is not None:
        abstract = " ".join(abstract.get_text().split(' ')[1:])
    return abstract


def get_venue(bs4obj):
    """
    Extract publication venue from arXiv.org paper page.
    :param bs4obj:
    :return:
    """
    venue = bs4obj.find("td", {"class": "tablecell comments mathjax"})
    if venue is not None:
        venue = venue.get_text().split(';')[0]
    return venue


def get_paper_info(url):
    """
    Extract paper information, title, abstract, and authors, from arXiv.org
    paper page.
    :param url:
    :return:
    """
    try:
        # html = urlopen("http://pythonscraping.com/pages/page1.html")
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
        print("The server could not be found.")
    else:
        bs4obj = BeautifulSoup(html)
        # Now, we can access individual element in the page
        authors = get_authors(bs4obj)
        title = get_title(bs4obj)
        abstract = get_abstract(bs4obj)
        # venue = get_venue(bs4obj)
        return title, authors, abstract

    return None, None, None


@login_required
def paper_create_from_arxiv(request):
    user = request.user

    if request.method == 'POST':
        # create the paper from the extracted data and send to
        # paper_form.html asking the user to verify
        print("{}".format(request.POST['url']))
        # get the data from arxiv
        url = request.POST['url']
        # check if url includes https, and if not add it
        if not url.startswith("https://"):
            url = "https://" + url
        # retrieve paper info. If the information cannot be retrieved from remote
        # server, then we will return an error message and redirect to paper_form.html.
        title, authors, abstract = get_paper_info(url)
        if title is None or authors is None or abstract is None:
            form = PaperImportForm()
            return render(request, 'paper_form.html', {'form': form, 'message': "Invalid source, please try again."})

        request.session['from_arxiv'] = True
        request.session['arxiv_title'] = title
        request.session['arxiv_abstract'] = abstract
        request.session['arxiv_url'] = url
        request.session['arxiv_authors'] = authors  # comma separate list of author names, first to last name

        print("Authors: {}".format(authors))

        return HttpResponseRedirect(reverse('paper_create'))
    else:  # GET
        request.session['from_arxiv'] = False
        form = PaperImportForm()

    return render(request, 'paper_form.html', {'form': form})


def _person_find(person_name, exact_match=False):
    """
    Searches the DB for a person whose name matches the given name
    :param person_name:
    :return:
    """
    person_name = person_name.lower()
    person_name_tokens = [w for w in person_name.split()]
    if exact_match:
        if len(person_name_tokens) > 2:
            query = (
                "MATCH (p:Person) WHERE  LOWER(p.last_name) IN { person_tokens } AND LOWER(p.first_name) IN { person_tokens } AND LOWER(p.middle_name) IN { person_tokens } RETURN p LIMIT 20")
        else:
            query = (
                "MATCH (p:Person) WHERE  LOWER(p.last_name) IN { person_tokens } AND LOWER(p.first_name) IN { person_tokens } RETURN p LIMIT 20")
    else:
        query = "MATCH (p:Person) WHERE  LOWER(p.last_name) IN { person_tokens } OR LOWER(p.first_name) IN { person_tokens } OR LOWER(p.middle_name) IN { person_tokens } RETURN p LIMIT 20"

    results, meta = db.cypher_query(query, dict(person_tokens=person_name_tokens))

    if len(results) > 0:
        print("Found {} matching people".format(len(results)))
        people = [Person.inflate(row[0]) for row in results]
        return people
    else:
        return None


#
# Dataset Views
#
def datasets(request):
    all_datasets = Dataset.nodes.order_by('-publication_date')[:50]
    return render(request, 'datasets.html', {'datasets': all_datasets})


def dataset_detail(request, id):
    # Retrieve the paper from the database
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        # There should be only one results because ID should be unique. Here we check that at
        # least one result has been returned and take the first result as the correct match.
        # Now, it should not happen that len(results) > 1 since IDs are meant to be unique.
        # For the MVP we are going to ignore the latter case and just continue but ultimately,
        # we should be checking for > 1 and failing gracefully.
        all_datasets = [Dataset.inflate(row[0]) for row in results]
        dataset = all_datasets[0]
    else:  # go back to the paper index page
        return render(request, 'datasets.html',
                      {'datasets': Dataset.nodes.all(), 'num_datasets': len(Dataset.nodes.all())})

    #
    # TO DO: Retrieve and list all papers that evaluate on this dataset.
    #

    request.session['last-viewed-dataset'] = id

    return render(request,
                  'dataset_detail.html',
                  {'dataset': dataset})


def _dataset_find(name, keywords):
    """
    Helper method for searching Neo4J DB for a dataset.

    :param name: Dataset name search query
    :param keywords: Dataset keywords search query
    :return:
    """
    dataset_name_tokens = [w for w in name.split()]
    dataset_keywords = [w for w in keywords.split()]
    datasets = []
    if len(dataset_keywords) > 0 and len(dataset_name_tokens) > 0:
        # Search using both the name and the keywords
        keyword_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in dataset_keywords) + '+.*'
        name_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in dataset_name_tokens) + '+.*'
        query = "MATCH (d:Dataset) WHERE  d.name =~ { name_query } AND d.keywords =~ { keyword_query} RETURN d LIMIT 25"
        results, meta = db.cypher_query(query, dict(name_query=name_query, keyword_query=keyword_query))
        if len(results) > 0:
            datasets = [Dataset.inflate(row[0]) for row in results]
            return datasets
    else:
        if len(dataset_keywords) > 0:
            # only keywords given
            dataset_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in dataset_keywords) + '+.*'
            query = "MATCH (d:Dataset) WHERE  d.keywords =~ { dataset_query } RETURN d LIMIT 25"
        else:
            # only name or nothing (will still return all datasets if name and
            # keywords fields are left empty and sumbit button is pressed.
            dataset_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in dataset_name_tokens) + '+.*'
            query = "MATCH (d:Dataset) WHERE  d.name =~ { dataset_query } RETURN d LIMIT 25"
            # results, meta = db.cypher_query(query, dict(dataset_query=dataset_query))

        results, meta = db.cypher_query(query, dict(dataset_query=dataset_query))
        if len(results) > 0:
            datasets = [Dataset.inflate(row[0]) for row in results]
            return datasets

    return datasets  # empty list


def dataset_find(request):
    """
    Searching for a dataset in the DB.

    :param request:
    :return:
    """
    message = None
    if request.method == 'POST':
        form = SearchDatasetsForm(request.POST)
        print("Received POST request")
        if form.is_valid():
            dataset_name = form.cleaned_data['name'].lower()
            dataset_keywords = form.cleaned_data['keywords'].lower()  # comma separated list

            datasets = _dataset_find(dataset_name, dataset_keywords)

            if len(datasets) > 0:
                return render(request, 'datasets.html', {'datasets': datasets})
            else:
                message = "No results found. Please try again!"
    elif request.method == 'GET':
        print("Received GET request")
        form = SearchDatasetsForm()

    return render(request, 'dataset_find.html', {'form': form, 'message': message})


@login_required
def dataset_create(request):
    user = request.user

    if request.method == 'POST':
        dataset = Dataset()
        dataset.created_by = user.id
        form = DatasetForm(instance=dataset, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('datasets_index'))
    else:  # GET
        form = DatasetForm()

    return render(request, 'dataset_form.html', {'form': form})


@login_required
def dataset_update(request, id):
    # retrieve paper by ID
    # https://github.com/neo4j-contrib/neomodel/issues/199
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        datasets = [Dataset.inflate(row[0]) for row in results]
        dataset = datasets[0]
    else:
        dataset = Dataset()

    # if this is POST request then process the Form data
    if request.method == 'POST':
        form = DatasetForm(request.POST)
        if form.is_valid():
            dataset.name = form.cleaned_data['name']
            dataset.keywords = form.cleaned_data['keywords']
            dataset.description = form.cleaned_data['description']
            dataset.publication_date = form.cleaned_data['publication_date']
            dataset.source_type = form.cleaned_data['source_type']
            dataset.website = form.cleaned_data['website']
            dataset.save()

            return HttpResponseRedirect(reverse('datasets_index'))
    # GET request
    else:
        query = "MATCH (a) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=id))
        if len(results) > 0:
            datasets = [Dataset.inflate(row[0]) for row in results]
            dataset = datasets[0]
        else:
            dataset = Dataset()
        form = DatasetForm(initial={'name': dataset.name,
                                    'keywords': dataset.keywords,
                                    'description': dataset.description,
                                    'publication_date': dataset.publication_date,
                                    'source_type': dataset.source_type,
                                    'website': dataset.website,
                                    }
                           )

    return render(request, 'dataset_update.html', {'form': form, 'dataset': dataset})


#
# Venue Views
#
def venues(request):
    all_venues = Venue.nodes.order_by('-publication_date')[:50]
    return render(request, 'venues.html', {'venues': all_venues})


def venue_detail(request, id):
    # Retrieve the paper from the database
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        # There should be only one results because ID should be unique. Here we check that at
        # least one result has been returned and take the first result as the correct match.
        # Now, it should not happen that len(results) > 1 since IDs are meant to be unique.
        # For the MVP we are going to ignore the latter case and just continue but ultimately,
        # we should be checking for > 1 and failing gracefully.
        all_venues = [Venue.inflate(row[0]) for row in results]
        venue = all_venues[0]
    else:  # go back to the paper index page
        return render(request, 'venues.html', {'venues': Venue.nodes.all(), 'num_venues': len(Venue.nodes.all())})

    #
    # TO DO: Retrieve all papers published at this venue and list them
    #
    request.session['last-viewed-venue'] = id
    return render(request,
                  'venue_detail.html',
                  {'venue': venue})


def venue_find(request):
    """
    Search for venue.
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = SearchVenuesForm(request.POST)
        if form.is_valid():
            # search the db for the venue
            # if venue found, then link with paper and go back to paper view
            # if not, ask the user to create a new venue
            english_stopwords = stopwords.words('english')
            venue_name = form.cleaned_data['venue_name'].lower()
            venue_publication_year = form.cleaned_data['venue_publication_year']
            # TO DO: should probably check that data is 4 digits...
            venue_name_tokens = [w for w in venue_name.split(' ') if not w in english_stopwords]
            venue_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in venue_name_tokens) + '+.*'
            query = "MATCH (v:Venue) WHERE v.publication_date =~ '" + venue_publication_year[0:4] + \
                    ".*' AND v.name =~ { venue_query } RETURN v"
            results, meta = db.cypher_query(query, dict(venue_publication_year=venue_publication_year[0:4],
                                                        venue_query=venue_query))
            if len(results) > 0:
                venues = [Venue.inflate(row[0]) for row in results]
                print("Found {} venues that match".format(len(venues)))
                return render(request, 'venues.html', {'venues': venues})
            else:
                # render new Venue form with the searched name as
                message = 'No matching venues found'

    if request.method == 'GET':
        form = SearchVenuesForm()
        message = None

    return render(request, 'venue_find.html', {'form': form, 'message': message})


@login_required
def venue_create(request):
    user = request.user

    if request.method == 'POST':
        venue = Venue()
        venue.created_by = user.id
        form = VenueForm(instance=venue, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('venues_index'))
    else:  # GET
        form = VenueForm()

    return render(request, 'venue_form.html', {'form': form})


@login_required
def venue_update(request, id):
    # retrieve paper by ID
    # https://github.com/neo4j-contrib/neomodel/issues/199
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        venues = [Venue.inflate(row[0]) for row in results]
        venue = venues[0]
    else:
        venue = Venue()

    # if this is POST request then process the Form data
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue.name = form.cleaned_data['name']
            venue.publication_date = form.cleaned_data['publication_date']
            venue.type = form.cleaned_data['type']
            venue.publisher = form.cleaned_data['publisher']
            venue.keywords = form.cleaned_data['keywords']
            venue.peer_reviewed = form.cleaned_data['peer_reviewed']
            venue.website = form.cleaned_data['website']
            venue.save()

            return HttpResponseRedirect(reverse('venues_index'))
    # GET request
    else:
        query = "MATCH (a) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=id))
        if len(results) > 0:
            venues = [Venue.inflate(row[0]) for row in results]
            venue = venues[0]
        else:
            venue = Venue()
        form = VenueForm(initial={'name': venue.name,
                                  'type': venue.type,
                                  'publication_date': venue.publication_date,
                                  'publisher': venue.publisher,
                                  'keywords': venue.keywords,
                                  'peer_reviewed': venue.peer_reviewed,
                                  'website': venue.website,
                                  }
                         )

    return render(request, 'venue_update.html', {'form': form, 'venue': venue})


#
# Comment Views
#
@login_required
def comments(request):
    """
    We should only show the list of comments if the user is admin. Otherwise, the user should
    be redirected to the home page.
    :param request:
    :return:
    """
    # Only superusers can view all the comments
    if request.user.is_superuser:
        return render(request, 'comments.html',
                      {'comments': Comment.nodes.all(), 'num_comments': len(Comment.nodes.all())})
    else:
        # other users are sent back to the paper index
        return HttpResponseRedirect(reverse('papers_index'))


@login_required
def comment_detail(request, id):
    # Only superusers can view comment details.
    if request.user.is_superuser:
        return render(request, 'comment_detail.html', {'comment': Comment.nodes.all()})
    else:
        # other users are sent back to the papers index
        return HttpResponseRedirect(reverse('papers_index'))


@login_required
def comment_create(request):
    user = request.user

    # Retrieve paper using paper id
    paper_id = request.session['last-viewed-paper']
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=paper_id))
    if len(results) > 0:
        all_papers = [Paper.inflate(row[0]) for row in results]
        paper = all_papers[0]
    else:  # just send him to the list of papers
        HttpResponseRedirect(reverse('papers_index'))

    if request.method == 'POST':
        comment = Comment()
        comment.created_by = user.id
        comment.author = user.username
        form = CommentForm(instance=comment, data=request.POST)
        if form.is_valid():
            # add link from new comment to paper
            form.save()
            comment.discusses.connect(paper)
            del request.session['last-viewed-paper']
            return redirect('paper_detail', id=paper_id)
    else:  # GET
        form = CommentForm()

    return render(request, 'comment_form.html', {'form': form})


@login_required
def comment_update(request, id):
    # retrieve paper by ID
    # https://github.com/neo4j-contrib/neomodel/issues/199
    query = "MATCH (a) WHERE ID(a)={id} RETURN a"
    results, meta = db.cypher_query(query, dict(id=id))
    if len(results) > 0:
        comments = [Comment.inflate(row[0]) for row in results]
        comment = comments[0]
    else:
        comment = Comment()

    # Retrieve paper using paper id
    paper_id = request.session['last-viewed-paper']

    # if this is POST request then process the Form data
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment.text = form.cleaned_data['text']
            # comment.author = form.cleaned_data['author']
            comment.save()
            # return HttpResponseRedirect(reverse('comments_index'))
            del request.session['last-viewed-paper']
            return redirect('paper_detail', id=paper_id)

    # GET request
    else:
        query = "MATCH (a) WHERE ID(a)={id} RETURN a"
        results, meta = db.cypher_query(query, dict(id=id))
        if len(results) > 0:
            comments = [Comment.inflate(row[0]) for row in results]
            comment = comments[0]
        else:
            comment = Comment()
        # form = CommentForm(initial={'author': comment.author,
        #                             'text': comment.text,
        #                             'publication_date': comment.publication_date,
        #                             }
        #                    )
        form = CommentForm(initial={'text': comment.text,
                                    'publication_date': comment.publication_date,
                                    }
                           )

    return render(request, 'comment_update.html', {'form': form, 'comment': comment})


#
# Utility Views (admin required)
#
@login_required
def build(request):
    try:
        d1 = Dataset()
        d1.name = 'Yelp'
        d1.source_type = 'N'
        d1.save()

        v1 = Venue()
        v1.name = 'Neural Information Processing Systems'
        v1.publication_date = date(2017, 12, 15)
        v1.type = 'C'
        v1.publisher = 'NIPS Foundation'
        v1.keywords = 'machine learning, machine learning, computational neuroscience'
        v1.website = 'https://nips.cc'
        v1.peer_reviewed = 'Y'
        v1.save()

        v2 = Venue()
        v2.name = 'International Conference on Machine Learning'
        v2.publication_date = date(2016, 5, 24)
        v2.type = 'C'
        v2.publisher = 'International Machine Learning Society (IMLS)'
        v2.keywords = 'machine learning, computer science'
        v2.peer_reviewed = 'Y'
        v2.website = 'https://icml.cc/2016/'
        v2.save()

        p1 = Paper()
        p1.title = 'The best paper in the world.'
        p1.abstract = 'Abstract goes here'
        p1.keywords = 'computer science, machine learning, graphs'
        p1.save()

        p1.evaluates_on.connect(d1)
        p1.was_published_at.connect(v1)

        p2 = Paper()
        p2.title = 'The second best paper in the world.'
        p2.abstract = 'Abstract goes here'
        p2.keywords = 'statistics, robust methods'
        p2.save()

        p2.cites.connect(p1)
        p2.was_published_at.connect(v2)

        p3 = Paper()
        p3.title = 'I wish I could write a paper with a great title.'
        p3.abstract = 'Abstract goes here'
        p3.keywords = 'machine learning, neural networks, convolutional neural networks'
        p3.save()

        p3.cites.connect(p1)
        p3.was_published_at.connect(v1)

        a1 = Person()
        a1.first_name = 'Pantelis'
        a1.last_name = 'Elinas'
        a1.save()

        a1.authors.connect(p1)

        a2 = Person()
        a2.first_name = "Ke"
        a2.last_name = "Sun"
        a2.save()

        a2.authors.connect(p1)
        a2.authors.connect(p2)

        a3 = Person()
        a3.first_name = "Bill"
        a3.last_name = "Gates"
        a3.save()

        a3.authors.connect(p3)
        a3.advisor_of.connect(a1)

        a4 = Person()
        a4.first_name = "Steve"
        a4.last_name = "Jobs"
        a4.save()

        a4.authors.connect(p2)
        a4.authors.connect(p3)

        a4.co_authors_with.connect(a3)

        c1 = Comment()
        c1.author = "Pantelis Elinas"
        c1.text = "This paper is flawless"
        c1.save()

        c1.discusses.connect(p1)

    except Exception:
        pass

    num_papers = len(Paper.nodes.all())
    num_people = len(Person.nodes.all())

    return render(request, 'build.html', {'num_papers': num_papers, 'num_people': num_people})