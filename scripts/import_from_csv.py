import pandas as pd
from sys import exit
from catalog.models import Person, Paper
from time import time


def load_authors(authors_ser):

    person_objects = []
    count = 0
    for authors in authors_ser:
        # if more than one authors the names are comma separated
        for author in authors.split(","):
            # print(author)
            # Create list of Person models so that we can call bulk_create
            person_objects.append(Person(name=author))
        # count += 1
        # if count > 3:
        #     break
    # print(person_objects)
    time_before = time()
    Person.objects.bulk_create(person_objects, ignore_conflicts=True)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Number of authors: {len(person_objects)}")
    print(
        f"Insert time per author: {(time_after-time_before)/len(person_objects)} secs"
    )


def load_papers(df):
    paper_objects = []
    # count = 0

    for index, row in df.iterrows():
        # count += 1
        paper_objects.append(
            Paper(
                title=row["title"],
                abstract=row["abstract"].replace('\n', ' '),
                download_link=row["pdf"],
                source_link=row["url"],
            )
        )
        # if count > 3:
        #     break
    time_before = time()
    Paper.objects.bulk_create(paper_objects, ignore_conflicts=True)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Number of papers: {len(paper_objects)}")
    print(
        f"Insert time per paper: {(time_after-time_before)/len(paper_objects)} secs"
    )

def test_load_authors():
    """ Simple test for script's behavior on duplicate names"""
    num_authors = 10000
    print("in test_load_authors()")
    authors = [Person(name="Pantelis Elinas"),] * num_authors
    # print(f"authors: {authors}")
    time_before = time()
    Person.objects.bulk_create(authors, ignore_conflicts=True)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Insert time per author: {(time_after-time_before)/num_authors} secs")


def main():
    filename = "/home/elinas/Projects/stellar-gnosis/scripts/papers.csv"

    df = pd.read_csv(filename)

    # load_authors(authors_ser=df["authors"])
    # test_load_authors()
    load_papers(df)


if __name__ == "__main__":
    exit(main())
