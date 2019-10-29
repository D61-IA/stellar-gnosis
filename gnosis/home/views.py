from django.shortcuts import render
from catalog.models import Paper
from catalog.forms import SearchPapersForm
from django.contrib.postgres.search import SearchQuery, SearchVector


def home(request):
    papers = Paper.objects.all()

    message = None

    if request.method == "POST":
        form = SearchPapersForm(request.POST)
        print("papers: Received POST request")
        if form.is_valid():
            # english_stopwords = stopwords.words("english")
            paper_title = form.cleaned_data["paper_title"].lower()
            print(f"Searching for paper using keywords {paper_title}")
            papers = Paper.objects.annotate(
                 search=SearchVector('title')
            ).filter(search=SearchQuery(paper_title, search_type='plain'))

            print(papers)

            if papers:
                return render(request, "paper_results.html", {"papers": papers, "form": form, "message": ""})
            else:
                message = "No results found. Please try again!"

    elif request.method == "GET":
        print("papers: Received GET request")
        form = SearchPapersForm()

    return render(request, 'home.html', {'papers': papers,
                                         'form': form,
                                         'message': message})