from typing import List, Optional, Dict, Generator, Set, Tuple
from itertools import chain, islice
import csv


def chunks(iterable, size):
    # Borrowed from here:
    # https://stackoverflow.com/a/24527424
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


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


def neighbours(edges: list, known_id) -> list:
    pass
