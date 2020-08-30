import csv

with open('/Users/av/Datasets/UnumDB/Graphs/PatentCitations/edges.csv') as csv_in:
    with open('/Users/av/Datasets/UnumDB/Graphs/PatentCitations/edges2.csv', 'w') as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)
        next(reader)
        writer.writerow(['first', 'second', 'weight'])
        for row in reader:
            row[2] = '1'
            writer.writerow(row)
