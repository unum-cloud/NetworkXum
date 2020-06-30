import csv
import json
import os


with open('/Users/av/Datasets/nlp-covid19-sections.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        'article_id',
        'article_title',
        'section_title',
        'section_text',
        'citations',
        'references',
    ])

    for subdir, _, files in os.walk('/Users/av/Datasets/nlp-covid19-jsons/'):
        for filename in files:

            j_source = dict()
            path_source = subdir + filename
            with open(path_source, 'r') as f_source:
                j_source = json.load(f_source)

            for section in j_source['body_text']:
                csv_writer.writerow([
                    j_source['paper_id'],
                    j_source['metadata']['title'],
                    section['section'],
                    section['text'],
                    len(section['cite_spans']),
                    len(section['ref_spans']),
                ])
