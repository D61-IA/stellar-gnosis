import pandas as pd
from sys import exit
from catalog.models import Person, Paper, PaperAuthorRelationshipData
from time import time


def load_authors(authors_ser):

    person_objects = []
    author_names = []
    for authors in authors_ser:
        # if more than one authors the names are comma separated
        for author in authors.split(","):
            # print(author)
            # Create list of Person models so that we can call bulk_create
            author_names.append(author)

    author_names = set(author_names)  # unique names
    person_objects = [Person(name=author) for author in author_names]

    # print(person_objects)
    time_before = time()
    # NOTE: We have to set ignore_conflicts to False if we want to get back the id for each
    # entry loaded into the DB. We need to make sure that author names are unique before
    # we call bulk_create or ingestion will fail with error.
    person_models = Person.objects.bulk_create(person_objects, ignore_conflicts=False)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Number of authors: {len(person_objects)}")
    print(
        f"Insert time per author: {(time_after-time_before)/len(person_objects)} secs"
    )

    # Create a dictionary mapping author names in author_names set to their corresponding DB
    # IDs so that we can quickly lookup the author ids when associating authors with papers.
    person_name_to_model_dict = dict(zip(author_names, person_models))

    return person_name_to_model_dict


def load_papers(df, limit=True):
    paper_objects = []
    count = 0

    for index, row in df.iterrows():
        count += 1
        paper_objects.append(
            Paper(
                title=row["title"],
                abstract=row["abstract"].replace("\n", " "),
                download_link=row["pdf"],
                source_link=row["url"],
            )
        )
        if limit and count > 3:
            break
    time_before = time()
    # NOTE: We have to set ignore_conflicts to False if we want to get back the id for each
    # entry loaded into the DB. We need to make sure that paper titles are unique before
    # we call bulk_create or ingestion will fail with error.
    paper_models = Paper.objects.bulk_create(paper_objects, ignore_conflicts=False)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Number of papers: {len(paper_objects)}")
    print(f"Insert time per paper: {(time_after-time_before)/len(paper_objects)} secs")

    return paper_models


def test_load_papers():
    """Simple test for loading a paper"""

    papers = [
        Paper(
            title="This is a paper",
            abstract="The meaning of life, universe and everything else.",
            download_link="https://scholar.google.com",
            source_link="https://scholar.google.com",
        )
    ]

    time_before = time()
    paper_models = Paper.objects.bulk_create(papers, ignore_conflicts=False)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Number of papers: {len(paper_models)}")
    print(f"Insert time per paper: {(time_after-time_before)/len(paper_models)} secs")

    return paper_models


def test_load_authors():
    """ Simple test for script's behavior on duplicate names"""
    print("in test_load_authors()")
    authors = [Person(name="Pantelis Elinas"), Person(name="Fiona Elliott")]
    num_authors = len(authors)
    # print(f"authors: {authors}")
    time_before = time()
    person_models = Person.objects.bulk_create(authors, ignore_conflicts=False)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Insert time per author: {(time_after-time_before)/num_authors} secs")
    return person_models


def test_load_paper_author_relationships(paper_models, person_models):
    paper_and_authors = [
        PaperAuthorRelationshipData(
            order=1, paper=paper_models[0], author=person_models[0]
        ),
        PaperAuthorRelationshipData(
            order=2, paper=paper_models[0], author=person_models[1]
        ),
    ]
    paper_and_author_models = PaperAuthorRelationshipData.objects.bulk_create(
        paper_and_authors, ignore_conflicts=False
    )

    return paper_and_author_models


def load_paper_author_relationships(df, paper_models, person_name_to_model_dict, limit=True):
    count = 0
    paper_and_authors = []
    # for each paper in the data
    for index, row in df.iterrows():
        count += 1
        # iterate over the authors keeping track of the order, 1st, 2nd, 3rd, etc.
        # print(f"row['authors']: {row['authors']}")
        for order, author in enumerate(row["authors"].split(",")):
            # print(f"\t\t author: {author}  order: {order}")
            paper_and_authors.append(
                PaperAuthorRelationshipData(
                    order=order+1, paper=paper_models[index], author=person_name_to_model_dict[author]
                ),
            )
        if limit and count > 3:
            break

    paper_and_author_models = PaperAuthorRelationshipData.objects.bulk_create(
        paper_and_authors, ignore_conflicts=False
    )

    return paper_and_author_models


def main():
    use_test_data = False
    filename = "/home/elinas/Projects/stellar-gnosis/scripts/papers.csv"

    # just delete all the papers and authors before moving on.
    Person.objects.all().delete()
    Paper.objects.all().delete()
    PaperAuthorRelationshipData.objects.all().delete()
    print("Deleted all existing objects from database.")

    if use_test_data:
        person_models = test_load_authors()
        print(f"{person_models}")
        for model in person_models:
            print(f"{model}")
            print(f"{model.pk} {model.id}")
            print(f"{type(model)}")
        #
        paper_models = test_load_papers()
        for model in paper_models:
            print(f"{model}")
            print(f"{model.pk} {model.id}")
            print(f"{type(model)}")

        paper_author_models = test_load_paper_author_relationships(
            paper_models, person_models
        )
        print(f"{paper_author_models}")
    else:
        limit=False
        df = pd.read_csv(filename, encoding='utf-8')
        print("Read pdf file.")
        person_name_to_model_dict = load_authors(authors_ser=df["authors"])
        print("Loaded authors")
        paper_models = load_papers(df, limit=limit)
        print("Loaded papers")
        load_paper_author_relationships(df, paper_models, person_name_to_model_dict, limit=limit)
        print("Done!")

if __name__ == "__main__":
    exit(main())
