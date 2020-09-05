from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence, Generator
from itertools import groupby, count, filterfalse, chain
import csv
import time
import concurrent
import math
from urllib.parse import urlparse
import random
from random import SystemRandom
from pathlib import Path
import collections

from PyWrappedHelpers import *


def is_sequence_of(objs, expected_class) -> bool:
    return isinstance(objs, collections.Sequence) and all([isinstance(obj, expected_class) for obj in objs])


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


def remove_duplicate_edges(es: Sequence[Edge]) -> Sequence[Edge]:
    ids = set()

    def false_if_exists(e: object) -> bool:
        if e._id < 0:
            ids.insert(e._id)
            return True
        return False
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


def yield_edges_from_csv(filepath: str, edge_type: type = Edge, is_directed=True) -> Generator[Edge, None, None]:
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # Skip the header line.
        next(reader)
        for idx, columns in enumerate(reader):
            if len(columns) < 2:
                continue
            # Check if the data isn't corrupt.
            first = int(columns[0])
            second = int(columns[1])
            has_weight = (len(columns) > 2 and len(columns[2]) > 0)
            w = float(columns[2]) if has_weight else 1.0
            yield edge_type(first=first, second=second, weight=w, _id=idx, is_directed=is_directed)


def yield_texts_from_sectioned_csv(filepath: str) -> Generator[Text, None, None]:
    last_text = str()
    last_path = str()
    allow_big_csv_fields()

    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        # Skip the header line.
        next(reader)
        for idx, columns in enumerate(reader):
            if len(columns) < 4:
                continue
            new_article_id = str(columns[0])
            new_text = str(columns[3])

            if new_article_id != last_path:
                if len(last_text) > 0:
                    yield Text(idx, last_text)
                last_path = new_article_id
                last_text = new_text
            else:
                last_text += new_text

        if len(last_text) > 0:
            yield Text(idx, last_text)


def yield_texts_from_directory(directory: str) -> Generator[Text, None, None]:
    idx = 0
    for path in Path(directory).iterdir():
        yield Text.from_file(path=path, _id=idx)
        idx += 1


def extract_database_name(url: str, default='graph') -> (str, str):
    url = urlparse(url)
    address = f'{url.scheme}://{url.netloc}'

    path_parts = url.path.split('/')
    path_parts = [v for v in path_parts if (v != '/' and v != '')]
    if len(path_parts) >= 1:
        if len(path_parts) > 1:
            print('Will avoid remaining url parts:', path_parts[2:])
        return address, path_parts[0].lower()
    else:
        return address, default


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
    return list(chain(*iterable))
