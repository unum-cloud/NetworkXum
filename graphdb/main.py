import csv
from itertools import chain, islice
import time

from rocks_nested import *
from rocks_adjacency import *
from mongo_adjacency import *
from sql_adjacency import *


class StatsCounter:
    def __init__(self):
        self.time_elapsed = 0
        self.count_operations = 0

    def handle(self, func):
        before = time.time()
        func()
        elapsed = before - time.time()
        self.time_elapsed += elapsed
        self.count_operations += 1

    def time_average(self):
        return self.time_elapsed / self.count_operations


def insert_separate(db, edges):
    # Measure time spent for each seprate insert
    pass


def insert_batched(db, edges, batch_size):
    # Split data into groups and pass like that
    pass


def remove_random_edges(db, edges):
    pass


def yield_edges_from(filepath: str):
    e = {
        'from': None,
        'to': None,
        'weight': 1.0,
    }
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for i, columns in enumerate(reader):
            if len(columns) < 2:
                continue
            e['from'] = int(columns[0])
            e['to'] = int(columns[1])
            e['weight'] = float(columns[2]) if len(columns) > 2 else 1.0
            yield e
            # Logging
            if i % 10000 == 0:
                print(f'-- progress: {i} edges')


def chunks(iterable, size=100):
    # Borrowed from here:
    # https://stackoverflow.com/a/24527424
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


stats_per_class_per_file = dict()
dbs = [
    GraphMongoAdjacency(
        url='mongodb://localhost:27017',
        db_name='graphdb',
        collection_name='orkut',
    )
]
files = [
    '/Users/av/Downloads/orkut/orkut.edges',
]
for f in files:
    # Create a counter.
    for db in dbs:
        stats_per_class_per_file[type(db)][f] = StatsCounter()
    dbs_empty = list()

    # Bulk-load data into DBs, if they are empty.
    if len(dbs_empty) > 0:
        for es in chunks(yield_edges_from(f), 10):
            es = list(es)
            for db in dbs_empty:
                counter = stats_per_class_per_file[type(db)]['import']
                counter.handle(lambda: db.insert_many(es))

# Benchmark groups in chronological order:
# - bulk load
# - lookups
# - edge removals
# - edge inserts
# - node removals

# Select this data beforehand to:
# - avoid affecting the runtime of benchmark.
# - perform same "random" operations on different DBs.
edges_to_insert_separately = []
edges_to_insert_batched = []
edges_to_lookup_sequential = []
edges_to_lookup_random = []
nodes_to_lookup_relations = []
nodes_to_lookup_from = []
nodes_to_lookup_to = []
nodes_to_lookup_friends_of_friends = []
nodes_to_compute_degree = []
nodes_to_compute_weight = []
edges_remove_separately = []
edges_remove_separately = []
