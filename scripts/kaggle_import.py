import pandas as pd
import re
import psycopg2
from datetime import datetime

df_paper = pd.read_csv('src/papers.csv')
df_author = pd.read_csv('src/authors.csv')
df_paper_author = pd.read_csv('src/paper_authors.csv')

# get author names that are tainted with random question marks
# df_qst_author = df_author[df_author['name'].str.contains(r'\?')]
# df_qst_author.to_csv('csv_qst_author')


def get_title_from_pdf_name(pdf_name):
    # remove '.pdf' from the name
    pdf_name = pdf_name[:-4]
    # find the first '-'
    idx = pdf_name.find('-')
    n = pdf_name[idx:]
    n = n.replace('-', ' ').strip()

    return n.title()


def add_author(paper_id):
    df_those_authors = df_paper_author.loc[df_paper_author['paper_id'] == paper_id]
    names = []

    for index, row in df_those_authors.iterrows():

        author_id = row['author_id']
        # get the paper title and its author name
        author_name = df_author.loc[df_author['id'] == author_id]['name'].iloc[0]

        if author_name is not None:

            names.append(author_name.strip())

    return names

start = -1
end = -1

info = []
other = []

for index, row in df_paper.iterrows():
    pdf_name = row['pdf_name']
    text = repr(row['paper_text'])
    paper_id = row['id']
    year = row['year']
    pdf_link = "https://papers.nips.cc/paper/" + pdf_name
    src_link = pdf_link[:-4]
    abstract = "Abstract not available"

    # get title from pdf_name
    title = get_title_from_pdf_name(pdf_name)

    # get 'abstract' with an optional ':' inside linebreaks, ignoring case
    start_text = re.search(r'\\n(?i)(abstract)(:)*?', text)
    if start_text is not None:
        start = start_text.start()
    if start != -1:
        text = text[start + 12:].lstrip(r'\\n')

        # get captialised words including space between linebreaks
        # number of appearance can be 0 (double linebreaks)
        # Adding ? after the qualifier makes it perform the match in non-greedy or minimal fashion;
        # as few characters as possible will be matched.
        end_text = re.search(r'\\n([A-Z ]*?)\\n', text)
        if end_text is not None:
            end = end_text.start()
        if end != -1:
            abstract = text[:end].replace('\\n', ' ').strip()

    # get the author names
    author_names = add_author(paper_id)
    entry = {'title': title, 'abstract': abstract, 'download_link': pdf_link, 'source_link': src_link, 'names': author_names}

    # if there is issue with getting the abstract, add to 'other' list
    if start == -1 or end == -1:
        # add paper text to entry
        entry['paper_text'] = repr(row['paper_text'])
        other.append(entry)
        print("-------" + str(paper_id) + "--------")
    else:
        info.append(entry)

    start = -1
    end = -1

df_info = pd.DataFrame(info)
# df_other = pd.DataFrame(other)

df_info.to_csv('csv_result')
# df_other.to_csv('csv_other')


def add_psql():
    connection = None
    sql_author = """INSERT INTO catalog_person(name, created_at) VALUES (%s, %s) RETURNING id"""
    sql_paper = """INSERT INTO catalog_paper(title, abstract, keywords, download_link, is_public, source_link, created_at, doi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    sql_paper_author = """INSERT INTO catalog_paperauthorrelationshipdata("order", author_id, paper_id) VALUES (%s, %s, %s)"""

    # set up postgres database connection
    try:
        connection = psycopg2.connect(user='gnosisuser',
                                      password='gnosis',
                                      host="localhost",
                                      port='5432',
                                      database='gnosistest')
        # create a new cursor
        cursor = connection.cursor()

        for index, row in df_info.iterrows():

            # insert authors
            names = row['names']
            a_ids = []
            for name in names:
                created_at = datetime.now()
                record = (name, created_at)
                cursor.execute(sql_author, record)

                author_id = cursor.fetchone()[0]
                a_ids.append(author_id)

                connection.commit()

            # insert paper
            title = row['title']
            abstract = row['abstract']
            download_link = row['download_link']
            source_link = row['source_link']
            keywords = ''
            is_public = True
            created_at = datetime.now()
            record = (title, abstract, keywords, download_link, is_public, source_link, created_at, title)
            cursor.execute(sql_paper, record)

            paper_id = cursor.fetchone()[0]
            connection.commit()

            # insert paper author relation
            for idx, a_id in enumerate(a_ids):
                record = (idx + 1, a_id, paper_id)
                cursor.execute(sql_paper_author, record)
                connection.commit()

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()


## uncomment the following if wish to add to database
# if __name__ == '__main__':
#     add_psql()

