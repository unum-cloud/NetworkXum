import time
import random
from random import SystemRandom
from typing import List
from copy import copy
import json
import platform
import os

from pygraphdb.graph_base import GraphBase
from pygraphdb.plain_sql import *
from pygraphdb.mongo_db import *
from helpers.shared import *

print('Welcome to GraphDB benchmarks!')
print('- Reading settings')
sampling_ratio = float(os.getenv('SAMPLING_RATIO', '0.01'))
sample_from_real_data = os.getenv('SAMPLE_FROM_REAL_DATA', '1') == '1'
count_nodes = int(os.getenv('COUNT_NODES', '0'))
count_edges = int(os.getenv('COUNT_EDGES', '0'))
count_finds = int(os.getenv('COUNT_FINDS', '10000'))
count_analytics = int(os.getenv('COUNT_ANALYTICS', '1000'))
count_changes = int(os.getenv('COUNT_CHANGES', '10000'))
mongo_url = os.getenv('URI_MONGO', 'mongodb://localhost:27017')
file_path = os.getenv('URI_FILE',
                      '/Users/av/Datasets/graph-communities/fb-pages-company.edges')

print('- Preparing global variables')
edges_to_query = []
nodes_to_query = []
nodes_to_analyze = []
edges_to_remove = []
edges_to_insert = []
stats_per_adapter_per_operation = dict()
benchmarks = []
# known_datasets = json.load(open('known_datasets.json', 'r'))


def restore_previous_stats():
    print('- Restoring previous benchmarks')
    benchmarks = json.load(open('benchmarks.json', 'r'))
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


def bench_matches(
    bench: obj,
    adapter_class: str,
    operation: str,
) -> bool:
    device_name = platform.node()
    if bench['device'] != device_name:
        return False
    if bench['adapter_class'] != adapter_class:
        return False
    if bench['operation'] != operation:
        return False
    return True


def update_stats(
    benchmarks: List[obj],
    adapter_class: str,
    operation: str,
    stats: StatsCounter,
) -> bool:
    device_name = platform.node()
    for bench in benchmarks:
        if bench_matches(bench, adapter_class, operation):
            bench = stats
            return True
    return False


def dump_updated_results():
    for a, stats_per_opertion in stats_per_adapter_per_operation:
        for o, stats in stats_per_opertion:
            update_stats(benchmarks, a, o, stats)
    json.dump(benchmarks, open('benchmarks.json', 'w'))


def select_tasks(
    file_path: str,
    count_nodes=0,
    count_finds=10000,
    count_analytics=1000,
    count_changes=10000,
):
    """
        Select this data beforehand to:
        - avoid affecting the runtime of benchmark.
        - perform same "random" operations on different DBs.
    """

    # Sample edges and node IDs.
    select_edges = list()
    select_nodes = set()
    if count_nodes == 0 or sample_from_real_data:
        # Sample from the actual file.
        rnd = SystemRandom()
        for e in yield_edges_from(file_path):
            if rnd.random() < sampling_ratio:
                select_edges.append(e)
                select_nodes.add(e['v_from'])
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
                'v_from': v_from,
                'v_to': v_to,
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
        e = db.find_directed(e['v_from'], e['v_to'])
        cnt += 1
    for e in edges_to_query[half:]:
        e = db.find_directed(e['v_to'], e['v_from'])
        cnt += 1
    return cnt


def find_edges_undirected(db) -> int:
    cnt = 0
    for e in edges_to_query:
        db.find_directed(e['v_from'], e['v_to'])
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
    for v in nodes_to_analyze:
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
restore_previous_stats()
select_tasks(file_path)
dbs = [
    MongoDB(
        url='mongodb://localhost:27017',
        db_name='graphdb',
        collection_name=filename,
    ),
    # PlainSQL(
    #     url='mysql://localhost:3306',
    #     table_name=filename,
    # ),
    # PlainSQL(
    #     url='postgres://localhost:5432',
    #     table_name=filename,
    # ),
]
for db in dbs:
    class_name = str(type(db))
    counters = stats_per_adapter_per_operation[class_name]
    benchmark(file_path, db, counters)
dump_updated_results()
