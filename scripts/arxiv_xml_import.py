# A script that given a directory with XML files each representing a paper from arXiv.org
# load the data, create Paper, Person and Paper-Person relationship models and uploads to
# the database.

import os
import click
import pandas as pd
import xml.etree.ElementTree as ET

input_dir = '/home/elinas/Projects/stellar-gnosis/arxiv_data'

# Requires input and output directory command line arguments, csv output filename as well as whether 
# to append to the output file or not (latter case creates a new file even if one already exists)
@click.command()
@click.option(
    "--input-dir",
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
    default='/home/elinas/Projects/stellar-gnosis/arxiv_data',
    help="Input directory",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
    default='/home/elinas/Projects/stellar-gnosis/arxiv_data',
    help="Output directory",
)
@click.option(
    "--csv",
    default='paper_data.csv',
    type=click.File('w')
)
@click.option(
    "--append/--create",
    default=False,
    help="Whether to append data to the output csv file or create a new one (overwrites if it already exists)",
)
def main(input_dir, output_dir, csv, append):
    print("Parameters:")
    print(f"input_dir: {input_dir}")
    print(f"output_dir: {output_dir}")
    print(f"csv: f{csv}")
    print(f"append: {append}")

    input_dir = os.path.abspath(input_dir)
    print(f"In main() with input dir {input_dir}")
    # get all xml files in input_dir
    xml_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    print(f"Found {len(xml_files)} files in input directory")

    data = []  # list of dictionaries holding data for each paper

    for index, xml_file in enumerate(xml_files):
        #print(f"File: {xml_file}")
        if index % 1000:
            print(f"Processed {index} xml files.")
        tree = ET.parse(os.path.join(input_dir, xml_file))
        root = tree.getroot()
        paper_data = {}
        for child in root:
            # print(child.tag)
            if child.tag.endswith('id'):
                paper_data['id'] = child.text.strip()
                paper_data['url'] = "https://arxiv.org/abs/"+child.text.strip()
                paper_data['pdf'] = "https://arxiv.org/pdf/"+child.text.strip() #+".pdf"
            elif child.tag.endswith('title'):
                # print(f"Title: {child.text}")
                paper_data['title'] = child.text.strip()
            elif child.tag.endswith('abstract'):
                paper_data['abstract'] = child.text.strip()
            elif child.tag.endswith('authors'):
                author_names = []
                for author in child:
                    # print(author)
                    name = []
                    for name_part in author:
                        if name_part.tag.endswith('forenames'):
                            name.insert(0, name_part.text.strip())
                        elif name_part.tag.endswith('keyname'):
                            name.append(name_part.text.strip())
                    author_names.append(' '.join(name))
                paper_data['authors'] = ','.join(author_names)
        data.append(paper_data)
    
    df = pd.DataFrame(data)
    print(df.head())
    df.to_csv(csv)

    return 0

if __name__=="__main__":
    exit(main())