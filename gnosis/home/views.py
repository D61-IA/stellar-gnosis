from django.shortcuts import render
from catalog.models import Paper, Person
from neomodel import db
from catalog.forms import SearchPapersForm
from nltk.corpus import stopwords


def home(request):
    num_papers = len(Paper.nodes.all())
    num_people = len(Person.nodes.all())

    recent_papers = Paper.nodes.order_by('-created')[:5]
    authors = [', '.join(get_paper_authors(paper)) for paper in recent_papers]

    papers = list(zip(recent_papers, authors))

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
                return render(request, 'paper_results.html', {'papers': papers, 'form': form, 'message': message})
            else:
                message = "No results found. Please try again!"

    elif request.method == 'GET':
        print("Received GET request")
        form = SearchPapersForm()

    return render(request, 'home.html', {'papers': papers,
                                         'num_papers': num_papers,
                                         'num_people': num_people,
                                         'form': form,
                                         'message': message})


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

