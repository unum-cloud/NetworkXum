import time
from random import SystemRandom
from copy import copy
import json
import platform
import os

from adapters.base import GraphBase
from adapters.sql import *
from adapters.mongo_adj import *
from adapters.rocks_nested import *
from adapters.rocks_adj import *
from adapters.neo4j import *
from shared import *

print('Welcome to GraphDB benchmarks!')
print('- Reading settings')
sampling_ratio = float(os.getenv('SAMPLING_RATIO', '0.01'))
count_nodes = int(os.getenv('COUNT_NODES', '0'))
count_edges = int(os.getenv('COUNT_EDGES', '0'))
count_finds = int(os.getenv('COUNT_FINDS', '0'))
count_analytics = int(os.getenv('COUNT_ANALYTICS', '0'))
count_changes = int(os.getenv('COUNT_CHANGES', '0'))
file_path = os.getenv('FILE_PATH', '0')

print('- Preparing global variables')
edges_to_query = []
nodes_to_query = []
nodes_to_analyze = []
edges_to_remove = []
edges_to_insert = []
stats_per_adapter_per_operation = dict()
known_datasets = json.load('known_datasets.json')


def restore_previous_stats(file_path='benchmarks.json'):
    print('- Resting previous benchmarks')
    benchmarks = json.load(file_path)
    device_name = platform.node()
    for bench in benchmarks:
        if bench['device'] != device_name:
            continue
        a = bench['adapter_class']
        o = bench['operation']
        t = bench['time_elapsed']
        c = bench['count_operations']
        s = StatsCounter(time_elapsed=t, count_operations=c)
        stats_per_adapter_per_operation[a][o] = s


def select_tasks(
    file_path: str,
    count_nodes=0,
    count_finds=10000,
    count_analytics=1000,
    count_changes=10000,
):
    '''
        Select this data beforehand to:
        - avoid affecting the runtime of benchmark.
        - perform same "random" operations on different DBs.
    '''

    # Sample edges and node IDs.
    select_edges = list()
    select_nodes = set()
    if count_nodes == 0:
        # Sample from the actual file.
        rnd = SystemRandom()
        for e in yield_edges_from(file_path):
            if rnd.random() < sampling_ratio:
                select_edges.append(e)
                select_nodes.add(e['from'])
        select_nodes = list(select_nodes)
        random.shuffle(select_edges)
        random.shuffle(select_nodes)
        count_finds = min(count_finds, len(select_nodes))
        count_analytics = min(count_analytics, len(select_nodes))
        count_changes = min(count_changes, len(select_edges))
    else:
        # Sample from the random distribution.
        count_max = max(count_finds, count_analytics, count_changes)
        while len(select_edges) < count_max:
            v_from = random.randrange(1, count_nodes)
            v_to = random.randrange(1, count_nodes)
            if v_from == v_to:
                continue
            if v_from in select_nodes:
                continue
            select_nodes.add(v_from)
            select_edges.append({
                'from': v_from,
                'to': v_to,
            })

    # Split query operations into groups.
    edges_to_query = random.sample(select_edges, count_finds)
    nodes_to_query = random.sample(select_nodes, count_finds)
    nodes_to_analyze = random.sample(select_nodes, count_analytics)

    # Split write operations into groups.
    edges_to_remove = select_edges[:count_changes]
    edges_to_insert = select_edges[:count_changes]
    # Following operations are no supported yet.
    # edges_to_insert_batched = select_edges[count_changes/2:count_changes]
    # nodes_to_remove = select_nodes[:count_changes]


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
    for e in edges_to_query:
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


def benchmark(file_path: str, db: GraphBase, stats: dict):
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
    def run(f):
        return StatsCounter().handle(f)

    # Bulk write operations.
    stats['bulk-load'] = run(lambda: db.import_file(file_path))
    stats['bulk-index'] = run(lambda: db.create_index())

    # Queries returning single object.
    stats['find-e-directed'] = run(lambda: find_edges_directed(db))
    stats['find-e-undirected'] = run(lambda: find_edges_undirected(db))

    # Queries returning collections.
    stats['find-es-from'] = run(lambda: find_edges_from(db))
    stats['find-es-to'] = run(lambda: find_edges_to(db))
    stats['find-es-related'] = run(lambda: find_edges_related(db))
    stats['find-vs-related'] = run(lambda: find_vertexes_related(db))
    stats['find-vs-related-related'] = run(lambda: find_vertexes_related2(db))

    # Queries returning stats.
    stats['count-v-degree'] = run(lambda: count_related(db))
    stats['count-v-followers'] = run(lambda: count_followers(db))
    stats['count-v-following'] = run(lambda: count_following(db))

    # Write operations.
    stats['remove-e'] = run(lambda: remove_edges(db))
    stats['insert-e'] = run(lambda: insert_edges(db))

    # This operation will alter the state of database,
    # changing the results on future runs.
    # stats['remove-v'] = run(lambda: find_edges_directed(db))


filename = file_path
select_tasks(file_path)
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
    class_name = type(db).__str__
    counters = stats_per_adapter_per_operation[class_name]
    benchmark(file_path, db, counters)
