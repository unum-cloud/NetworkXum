import csv
import sqlite3

file_in = open('/Users/av/Datasets/UnumDB/Articles/OldNewspapers/all.tsv', 'r')
file_out = open(
    '/Users/av/Datasets/UnumDB/Articles/OldNewspapers/all.csv', 'w')

reader = csv.reader(file_in, delimiter='\t')
writer = csv.writer(file_out, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_ALL)

next(reader)
writer.writerow(['language', 'source', 'date', 'section_text'])

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


for row_in in reader:
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
