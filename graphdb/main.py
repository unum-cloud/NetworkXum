import time

from g_rocks_nested import *
from g_rocks_adj import *
from g_mongo_adj import *
from g_sql import *


def insert_separate(db, edges):
    # Measure time spent for each seprate insert
    pass


def insert_batched(db, edges, batch_size):
    # Split data into groups and pass like that
    pass


def remove_random_edges(db, edges):
    pass


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
# - index construction
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
