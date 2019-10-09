from django.shortcuts import render
from catalog.models import Paper, Person, Venue, Dataset, Code
from neomodel import db
from catalog.forms import SearchPapersForm, SearchAllForm
from nltk.corpus import stopwords


def home(request):
    num_papers = len(Paper.nodes.all())
    num_people = len(Person.nodes.all())

    recent_papers = Paper.nodes.order_by('-created')[:5]
    authors = [', '.join(get_paper_authors(paper)) for paper in recent_papers]

    all_authors = []

    for s in authors:
        if len(s) > 0:
            temp = s.split(', ')
            all_authors = all_authors + temp

    recent_authors = all_authors[:9]

    papers = list(zip(recent_papers, authors))
    form = SearchAllForm(request.POST)
    message = None
    paper_results = []
    person_results = []
    venue_results =[]
    dataset_results = []
    codes_results = []

    form.fields['search_type'].initial = ['all']

    if request.method == 'POST':

        print("Received POST request")
        if form.is_valid():
            english_stopwords = stopwords.words('english')
            search_filter = form.cleaned_data['search_type']
            search_keywords = form.cleaned_data['search_keywords'].lower()
            search_keywords_tokens = [w for w in search_keywords.split(' ') if not w in english_stopwords]

            all_query = '(?i).*' + '+.*'.join('(' + w + ')' for w in search_keywords_tokens) + '+.*'
            query = "match (n) with n, [x in keys(n) WHERE n[x]=~ { all_query }] as doesMatch where size(doesMatch) > 0 return n"
            #query = "MATCH (p:Paper) WHERE  p.title =~ { paper_query } OR p.abstract =~ { paper_query }  RETURN p LIMIT 25"
            #print("Cypher query string {}".format(query))
            results, meta = db.cypher_query(query, dict(all_query=all_query))

            #print("Results: ", results)
            if len(results) > 0:

                if search_filter == 'all':
                    print("{} match(es) found ".format(len(results)))

                    for row in results:
                        for label in row[0].labels:

                            if label == 'Paper':
                                paper_results.append(Paper.inflate(row[0]))

                            elif label == 'Person':
                                person_results.append(Person.inflate(row[0]))
                                print(person_results)

                            elif label == 'Venue':
                                venue_results.append(Venue.inflate(row[0]))

                            elif label == 'Dataset':
                                dataset_results.append(Dataset.inflate(row[0]))

                            elif label == 'Code':
                                codes_results.append(Code.inflate(row[0]))

                    #papers = [Paper.inflate(row[0]) for row in results]
                    #search_results = paper_results.append(person_results.append(venue_results.append(
                    #   dataset_results.append(codes_results))))
                    print("Going to all results page..........")
                    return render(request, 'all_results.html', {'paper_results': paper_results,
                                                            'person_results': person_results, 'venue_results': venue_results,
                                                            'dataset_results': dataset_results, 'codes_results': codes_results,
                                                            'form': form, 'message': message})

                elif search_filter == 'papers':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Paper':
                                paper_results.append(Paper.inflate(row[0]))

                    if len(paper_results) > 0 :
                        print("Found {} matching papers".format(len(paper_results)))
                        return render(request, "paper_results.html",
                                              {"paper_results": paper_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'home.html', {'papers': papers, 'num_papers': num_papers,
                                      'num_people': num_people, 'form': form, 'message': message})

                elif search_filter == 'people':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Person':
                                person_results.append(Person.inflate(row[0]))

                    if len(person_results) > 0 :
                        print("Found {} matching papers".format(len(person_results)))
                        return render(request, "people_results.html",
                                        {"person_results": person_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'home.html', {'papers': papers, 'num_papers': num_papers,
                                        'num_people': num_people, 'form': form, 'message': message})

                elif search_filter == 'venues':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Venue':
                                venue_results.append(Venue.inflate(row[0]))

                    if len(venue_results) > 0 :
                        print("Found {} matching papers".format(len(venue_results)))
                        return render(request, "venue_results.html",
                                      {"venue_results": venue_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'home.html', {'papers': papers, 'num_papers': num_papers,
                                        'num_people': num_people, 'form': form, 'message': message})

                elif search_filter == 'datasets':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Dataset':
                                dataset_results.append(Dataset.inflate(row[0]))

                    if len(dataset_results) > 0 :
                        print("Found {} matching papers".format(len(dataset_results)))
                        return render(request, "dataset_results.html",
                                          {"dataset_results": dataset_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'home.html', {'papers': papers, 'num_papers': num_papers,
                                        'num_people': num_people, 'form': form, 'message': message})

                elif search_filter == 'codes':
                    for row in results:
                        for label in row[0].labels:
                            if label == 'Code':
                                codes_results.append(Code.inflate(row[0]))

                    if len(codes_results) > 0 :
                        print("Found {} matching papers".format(len(codes_results)))
                        return render(request, "code_results.html",
                                  {"codes_results": codes_results, "form": form, "message": ""})
                    else:
                        message = "No results found. Please try again!"
                        return render(request, 'home.html', {'papers': papers, 'num_papers': num_papers,
                                        'num_people': num_people, 'form': form, 'message': message})



            else:
                message = "No results found. Please try again!"

    elif request.method == 'GET':
        print("Received GET request")
        form = SearchAllForm()

    print(message)
    return render(request, 'home.html', {'papers': papers, 'num_papers': num_papers,
                                             'num_people': num_people, 'form': form, 'message': message, 'recent_authors': recent_authors})



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
