import time
from random import SystemRandom
from copy import copy

from adapters.base import GraphBase
from adapters.sql import *
from adapters.mongo_adj import *
from adapters.rocks_nested import *
from adapters.rocks_adj import *
from adapters.neo4j import *
from shared import *

sampling_ratio = 0.01
stats_per_class_per_file = dict()
files = [
    '/Users/av/Downloads/orkut/orkut.edges',
]


def select_tasks(filepath: str):
    '''
        Select this data beforehand to:
        - avoid affecting the runtime of benchmark.
        - perform same "random" operations on different DBs.
    '''

    # Sample edges and node IDs from the file.
    select_edges = list()
    select_nodes = set()
    rnd = SystemRandom()
    for e in yield_edges_from(filepath):
        if rnd.random() < sampling_ratio:
            select_edges.append(e)
            select_nodes.add(e['from'])
    select_nodes = list(select_nodes)
    random.shuffle(select_edges)
    random.shuffle(select_nodes)
    count_finds = min(10000, len(select_nodes))
    count_analytics = min(1000, len(select_nodes))
    count_changes = min(10000, len(select_edges))

    # Split write operations into groups.
    edges_to_remove = select_edges[:count_changes]
    edges_to_insert = select_edges[:count_changes/2]
    # Following operations are no supported yet.
    # edges_to_insert_batched = select_edges[count_changes/2:count_changes]
    # nodes_to_remove = select_nodes[:count_changes]

    # Split query operations into groups.
    edges_to_query = random.sample(select_edges, count_finds)
    nodes_to_query = random.sample(select_nodes, count_finds)
    nodes_to_analyze = random.sample(select_nodes, count_analytics)


def find_edges_directed(db) -> int:
    # Try both existing and potentially missing edges
    half = len(edges_to_query) / 2
    cnt = 0
    for e in edges_to_query[:half]:
        e = db.find_directed(e['from'], e['to'])
        cnt += 1
    for e in edges_to_query[half:]:
        e = db.find_directed(e['to'], e['from'])
        cnt += 1
    return cnt


def find_edges_undirected(db) -> int:
    cnt = 0
    for e in edges_to_find_undirected:
        db.find_directed(e['from'], e['to'])
        cnt += 1
    return cnt


def find_edges_related(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.edges_related(v)
        cnt += 1
    return cnt


def find_edges_from(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.edges_from(v)
        cnt += 1
    return cnt


def find_edges_to(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.edges_to(v)
        cnt += 1
    return cnt


def find_vertexes_related(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.vertexes_related(v)
        cnt += 1
    return cnt


def count_related(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.count_related(v)
        cnt += 1
    return cnt


def count_followers(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.count_followers(v)
        cnt += 1
    return cnt


def count_following(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.count_following(v)
        cnt += 1
    return cnt


def find_vertexes_related2(db) -> int:
    cnt = 0
    for v in nodes_to_query:
        db.vertexes_related_to_related(v)
        cnt += 1
    return cnt


def remove_edges(db) -> int:
    cnt = 0
    for e in edges_to_remove:
        db.delete(e)
        cnt += 1
    return cnt


def insert_edges(db) -> int:
    cnt = 0
    for e in edges_to_insert:
        db.insert(e)
        cnt += 1
    return cnt


def benchmark(filepath: str, db: GraphBase, stats: dict):
    # Benchmark groups in chronological order:
    # --
    # - bulk load
    # - index construction
    # --
    # - lookups
    # - analytics
    # --
    # - edge removals
    # - edge inserts
    # - optional node removals
    # --

    # Bulk write operations.
    stats['bulk-load'].handle(lambda: db.import_file(filepath))
    stats['bulk-index'].handle(lambda: db.create_index())

    # Queries returning single object.
    stats['find-e-directed'].handle(lambda: find_edges_directed(db))
    stats['find-e-undirected'].handle(lambda: find_edges_undirected(db))

    # Queries returning collections.
    stats['find-es-from'].handle(lambda: find_edges_from(db))
    stats['find-es-to'].handle(lambda: find_edges_to(db))
    stats['find-es-related'].handle(lambda: find_edges_related(db))
    stats['find-vs-related'].handle(lambda: find_vertexes_related(db))
    stats['find-vs-related-related'].handle(lambda: find_vertexes_related2(db))

    # Queries returning stats.
    stats['count-v-degree'].handle(lambda: count_related(db))
    stats['count-v-followers'].handle(lambda: count_followers(db))
    stats['count-v-following'].handle(lambda: count_following(db))

    # Write operations.
    stats['remove-e'].handle(lambda: remove_edges(db))
    stats['insert-e'].handle(lambda: insert_edges(db))

    # This operation will alter the state of database,
    # changing the results on future runs.
    # stats['remove-v'].handle(lambda: find_edges_directed(db))


for filepath in files:
    filename = filepath
    select_tasks(filepath)
    dbs = [
        GraphMongoAdjacency(
            url='mongodb://localhost:27017',
            db_name='graphdb',
            collection_name=filename,
        ),
        # GraphSQL(
        #     url='mysql://localhost:27017',
        #     table_name=filename
        # ),
        # GraphSQL(
        #     url='postgres://localhost:27017',
        #     table_name=filename
        # ),
    ]
    for db in dbs:
        counter = StatsCounter()
        benchmark(filepath, db, counter)
        stats_per_class_per_file[type(db)][filepath] = counter
