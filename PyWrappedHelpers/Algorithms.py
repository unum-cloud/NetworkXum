from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence, Generator
from itertools import groupby, count, filterfalse
import csv
import time
import concurrent
import math
from urllib.parse import urlparse
from random import SystemRandom

from PyWrappedHelpers.Edge import Edge
from PyWrappedHelpers.TextFile import TextFile


def map_compact(func, os: Sequence[object]) -> Sequence[object]:
    # if isinstance(os, Generator):
    #     for o in os:
    #         o_new = func(o)
    #         if o_new is None:
    #             continue
    #         yield o_new
    # else:
    os_new = list()
    for o in os:
        o_new = func(o)
        if o_new is None:
            continue
        os_new.append(o_new)
    return os_new


def remove_duplicate_edges(es: Sequence[object]) -> Sequence[object]:
    ids = set()

    def false_if_exists(e: object) -> bool:
        if '_id' in e:
            return False
        ids.add(e['_id'])
        return True
    return filterfalse(false_if_exists, es)


def chunks(iterable, size) -> Generator[list, None, None]:
    current = list()
    for v in iterable:
        if len(current) == size:
            yield current
            current = list()
        current.append(v)
    if len(current) > 0:
        yield current


def yield_edges_from_csv(filepath: str, edge_type: type = Edge, directed=True) -> Generator[object, None, None]:
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # Skip the header line.
        next(reader)
        for idx, columns in enumerate(reader):
            if len(columns) < 2:
                continue
            # Check if the data isn't corrupt.
            v1 = int(columns[0])
            v2 = int(columns[1])
            has_weight = (len(columns) > 2 and len(columns[2]) > 0)
            w = float(columns[2]) if has_weight else 1.0
            yield edge_type(v1=v1, v2=v2, weight=w, _id=idx, directed=directed)


def yield_texts_from_sectioned_csv(filepath: str) -> Generator[TextFile, None, None]:
    current = TextFile()

    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # Skip the header line.
        next(reader)
        for idx, columns in enumerate(reader):
            if len(columns) < 4:
                continue
            new_article_id = str(columns[0])
            if new_article_id != current.path:
                if len(current.content.get('plain', '')):
                    yield current
                current.content['plain'] = str()
            current.path = new_article_id
            current.content['plain'] += str(columns[3])

    if len(current.content.get('plain', '')):
        yield current


def export_edges_into_graph(filepath: str, g) -> int:
    e_type = type(g).__edge_type__
    chunk_len = type(g).__max_batch_size__
    count_edges_added = 0
    starting_id = g.biggest_edge_id()
    for es in chunks(yield_edges_from_csv(filepath, e_type), chunk_len):
        for i, e in enumerate(es):
            es[i]['_id'] += starting_id
        count_edges_added += g.upsert_edges(es)
    return count_edges_added


def export_edges_into_graph_parallel(filepath: str, g, thread_count=8) -> int:
    e_type = type(g).__edge_type__
    batch_per_thread = type(g).__max_batch_size__
    chunk_len = thread_count * batch_per_thread
    count_edges_before = g.count_edges()
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        for es in chunks(yield_edges_from_csv(filepath, e_type), chunk_len):
            x_len = int(math.ceil(len(es) / thread_count))
            es_per_thread = [es[x:x+x_len] for x in range(0, len(es), x_len)]
            print(f'-- Importing part: {x_len} rows x {thread_count} threads')
            executor.map(g.upsert_edges, es_per_thread)
            executor.shutdown(wait=True)
    return g.count_edges() - count_edges_before


def extract_database_name(url: str, default='graph') -> str:
    url_parts = urlparse(url).path
    url_parts = url_parts.split('/')
    url_parts = [v for v in url_parts if (v != '/' and v != '')]
    if len(url_parts) >= 1:
        if len(url_parts) > 1:
            print('Will avoid remaining url parts:', url_parts[2:])
        return url_parts[0]
    else:
        return default


def sample_reservoir(iterable, count_needed: int) -> list:
    count_seen = 0
    ret = list()
    for e in iterable:
        count_seen += 1
        if len(ret) < count_needed:
            ret.append(e)
        else:
            s = int(random.random() * count_seen)
            if s < count_needed:
                ret[s] = e
    return ret


def class_name(cls: type) -> str:
    if isinstance(cls, type):
        return cls.__name__
    else:
        return cls.__class__.__name__


def flatten(iterable) -> list:
    return reduce(lambda x, y: x+y, iterable)
