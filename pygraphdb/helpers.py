from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
from itertools import groupby, count
import csv
import time

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
        for i, columns in enumerate(reader):
            if i < lines_to_skip:
                continue
            if len(columns) < 2:
                continue
            v1 = int(columns[0])
            v2 = int(columns[1])
            w = float(columns[2]) if len(columns) > 2 else 1.0
            yield Edge(v1, v2, w)


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
