from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
from itertools import groupby, count
import csv
import time
import concurrent
import math
from urllib.parse import urlparse

from pygraphdb.edge import Edge


def chunks(iterable, size) -> Generator[list, None, None]:
    current = list()
    for v in iterable:
        if len(current) == size:
            yield current
            current = list()
        current.append(v)
    if len(current) > 0:
        yield current


def yield_edges_from(filepath: str) -> Generator[Edge, None, None]:
    lines_to_skip = 0
    if filepath.endswith('.mtx'):
        lines_to_skip = 2
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        line_idx = 0
        for columns in reader:
            if line_idx < lines_to_skip:
                line_idx += 1
                continue
            line_idx += 1
            if len(columns) < 2:
                continue
            # Skip header row.
            if (columns[0] == 'v_from'):
                continue
            # Check if the data isn't corrupt.
            v1 = int(columns[0])
            v2 = int(columns[1])
            has_weight = (len(columns) > 2 and len(columns[2]) > 0)
            w = float(columns[2]) if has_weight else 1.0
            yield Edge(v1, v2, w)

# def deduplicate_chunks()
#         es_filtered = list()
#         es_ids = set()
#         for e in es:
#             e_new = self._to_sql(e, e_type=e_type)
#             if e_new['_id'] in es_ids:
#                 continue
#             es_ids.add(e_new['_id'])
#             es_filtered.append(e_new)


def export_edges_into_graph(filepath: str, g) -> int:
    chunk_len = type(g).__max_batch_size__
    count_edges_added = 0
    for es in chunks(yield_edges_from(filepath), chunk_len):
        count_edges_added += g.insert_edges(es)
    return count_edges_added


def export_edges_into_graph_parallel(filepath: str, g, thread_count=8) -> int:
    batch_per_thread = type(g).__max_batch_size__
    chunk_len = thread_count * batch_per_thread
    count_edges_before = g.count_edges()
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        for es in chunks(yield_edges_from(filepath), chunk_len):
            x_len = int(math.ceil(len(es) / thread_count))
            es_per_thread = [es[x:x+x_len] for x in range(0, len(es), x_len)]
            print(f'-- Importing part: {x_len} rows x {thread_count} threads')
            executor.map(g.insert_edges, es_per_thread)
            executor.shutdown(wait=True)
    return g.count_edges() - count_edges_before


def extract_database_name(url: str) -> str:
    url_parts = urlparse(url).path
    url_parts = url_parts.split('/')
    url_parts = [v for v in url_parts if (v != '/' and v != '')]
    if len(url_parts) >= 1:
        if len(url_parts) > 1:
            print('Will avoid remaining url parts:', url_parts[2:])
        return url_parts[0]
    else:
        return 'graph'


class StatsCounter:
    def __init__(self, time_elapsed=0, count_operations=0):
        self.time_elapsed = time_elapsed
        self.count_operations = count_operations

    def handle(self, func):
        before = time.time()
        ops = func()
        elapsed = time.time() - before
        self.time_elapsed += elapsed
        assert isinstance(ops, int), \
            'Return value must contain the number of operations'
        self.count_operations += ops

    def secs_per_op(self) -> float:
        if (self.count_operations == 0):
            return 0
        return self.time_elapsed / self.count_operations

    def msecs_per_op(self) -> float:
        if (self.count_operations == 0):
            return 0
        return self.secs_per_op() / 1000.0

    def ops_per_sec(self) -> float:
        if (self.count_operations == 0):
            return 0
        return self.count_operations / self.time_elapsed

    def __repr__(self) -> str:
        return f'<StatsCounter (#{self.count_operations} ops averaging ~{self.msecs_per_op()} msecs)>'
