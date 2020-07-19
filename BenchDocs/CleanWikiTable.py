import csv
import sqlite3

file_in = sqlite3.connect('/Users/av/Datasets/UnumDB/EnglishWikipedia/all.db')
file_out = open('/Users/av/Datasets/UnumDB/EnglishWikipedia/all.csv', 'w')

writer = csv.writer(file_out, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_ALL)


# https://www.geeksforgeeks.org/python-replace-multiple-occurrence-of-character-by-single/
def replace_repetitions(s: str, ch) -> str:
    new_str = []
    l = len(s)
    for i in range(len(s)):
        if (s[i] == ch and i != (l-1) and
                i != 0 and s[i + 1] != ch and s[i-1] != ch):
            new_str.append(s[i])
        elif s[i] == ch:
            if ((i != (l-1) and s[i + 1] == ch) and
                    (i != 0 and s[i-1] != ch)):
                new_str.append(s[i])
        else:
            new_str.append(s[i])
    return (''.join(i for i in new_str))


writer.writerow(['article_id', 'article_title',
                 'section_title', 'section_text'])

for row_in in file_in.cursor().execute('SELECT * FROM ARTICLES'):
    row_out = list()

    for cell in row_in:
        cell = str(cell).replace('\r', ' ')
        cell = cell.replace('\n', ' ')
        cell = cell.replace('\"', '\'')
        cell = replace_repetitions(cell, '\'')
        cell = cell.strip()
        row_out.append(cell)
    writer.writerow(row_out)

file_out.close()
