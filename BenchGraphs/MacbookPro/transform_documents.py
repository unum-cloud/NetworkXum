
import json
import os


def print_author_name(author: dict) -> str:
    return '{} {}'.format(author['first'], author['last'])


def transform_json(j_source: dict) -> dict:
    j_target = dict()
    j_target['_id'] = j_source['paper_id']
    j_target['title'] = j_source['metadata']['title']

    substrings = list()
    for obj in j_source['abstract']:
        substrings.append(obj['text'])
        substrings.append('\n')
    for obj in j_source['body_text']:
        substrings.append(obj['section'])
        substrings.append('\n')
        substrings.append(obj['text'])
        substrings.append('\n')
    j_target['text'] = '\n'.join(substrings)
    j_target['count_sections'] = len(j_source['body_text'])
    j_target['count_symbols'] = len(j_target['text'])
    j_target['count_bib_entries'] = len(j_source['bib_entries'])

    authors = j_source['metadata']['authors']
    j_target['count_authors'] = len(authors)
    if len(authors) > 0:
        j_target['first_author'] = print_author_name(authors[0])
        j_target['authors'] = ', '.join(map(print_author_name, authors))
    else:
        j_target['first_author'] = ''
        j_target['authors'] = ''
    return j_target


dir_source = '/Users/av/Datasets/nlp-covid19/original/'
dir_target = '/Users/av/Datasets/nlp-covid19/shallow/'

for subdir, dirs, files in os.walk(dir_source):
    for filename in files:

        j_source = dict()
        path_source = subdir + filename
        with open(path_source, 'r') as f_source:
            j_source = json.load(f_source)

        j_target = transform_json(j_source)
        path_target = dir_target + filename
        with open(path_target, 'w') as f_target:
            json.dump(j_target, f_target,
                      sort_keys=True,
                      indent=4,
                      ensure_ascii=False)
