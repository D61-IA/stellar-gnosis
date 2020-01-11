import pandas as pd
from sys import exit
from catalog.models import Person
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
    print(person_objects)
    time_before = time()
    Person.objects.bulk_create(person_objects, ignore_conflicts=True)
    time_after = time()
    print(f"Insert took time {time_after-time_before} secs")
    print(f"Number of authors: {len(person_objects)}")
    print(f"Insert time per author: {(time_after-time_before)/len(person_objects)} secs")


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

    load_authors(authors_ser=df['authors'])
    #test_load_authors()


if __name__ == "__main__":
    exit(main())
