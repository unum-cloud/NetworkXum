from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
from itertools import chain, islice
import csv
import time


def chunks(iterable, size):
    # Borrowed from here:
    # https://stackoverflow.com/a/24527424
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


def yield_edges_from(filepath: str):
    e = {
        'v_from': None,
        'v_to': None,
        'weight': 1.0,
    }
    lines_to_skip = 0
    if filepath.endswith('.mtx'):
        lines_to_skip = 2
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for i, columns in enumerate(reader):
            if i < lines_to_skip:
                continue
            if len(columns) < 2:
                continue
            e['v_from'] = int(columns[0])
            if e['v_from'] is None:
                continue
            e['v_to'] = int(columns[1])
            if e['v_to'] is None:
                continue
            e['weight'] = float(columns[2]) if len(columns) > 2 else 1.0
            yield e


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
        return self.time_elapsed / self.count_operations

    def msecs_per_op(self) -> float:
        return self.secs_per_op() / 1000.0

    def ops_per_sec(self) -> float:
        return self.count_operations / self.time_elapsed
